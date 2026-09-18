from dataclasses import dataclass
from pathlib import Path
import json,time,uuid
import cv2,numpy as np
from backend.preprocessing.illumination import representation,select_band,to_gray_uint8
from backend.preprocessing.sun_geometry import sun_normalize,illumination_descriptor
from backend.features.detector import detect,terrain_type
from backend.matching.classical import ratio_match
from backend.matching.spatial import diverse_subset
from backend.matching.orchestrator import choose_engine
from backend.geometry.estimate import estimate_adaptive,reprojection_errors,warp_points
from backend.geometry.quality import quality_gate,calibrated_confidence
from backend.refinement.subpixel import refine_lk
from backend.evaluation.metrics import summarize,coverage

@dataclass
class RegistrationResult:
    id:str; metrics:dict; status:str; paths:dict; explanation:str; metadata:dict; correspondences:list

def _resize(image,factor): return image if factor==1 else cv2.resize(image,None,fx=factor,fy=factor,interpolation=cv2.INTER_AREA)

def _candidate(source,target,method,rep,factor,grid,spatial_selection,sun_source=None,sun_target=None):
    src=_resize(representation(source,rep),factor); tgt=_resize(representation(target,rep),factor)
    src=sun_normalize(src,*sun_source) if sun_source else src; tgt=sun_normalize(tgt,*sun_target) if sun_target else tgt
    a,b=detect(src,method),detect(tgt,method); raw=ratio_match(a,b)
    matches,cells=diverse_subset(raw,a.keypoints,src.shape,grid=grid) if spatial_selection else (raw,{})
    geo=estimate_adaptive(a.keypoints,b.keypoints,matches,threshold=max(1.5,3.0*factor))
    errors=reprojection_errors(a.keypoints,b.keypoints,matches,geo.matrix,geo.model)
    score=int(geo.inlier_mask.sum())*(float(geo.inlier_mask.mean()) if len(matches) else 0)-(.05*float(np.nanmedian(errors)) if np.isfinite(errors).any() else 100)
    return {'src':src,'tgt':tgt,'a':a,'b':b,'raw':raw,'matches':matches,'geo':geo,'errors':errors,'score':score,'factor':factor,'rep':rep,'cells':cells}

def _warp(src,tgt,matrix,model):
    if matrix is None: return cv2.resize(src,(tgt.shape[1],tgt.shape[0]),interpolation=cv2.INTER_LINEAR)
    if model=='homography': return cv2.warpPerspective(src,matrix,(tgt.shape[1],tgt.shape[0]))
    return cv2.warpAffine(src,matrix,(tgt.shape[1],tgt.shape[0]))

def _write_images(out,src,tgt,best,final_matrix,final_model,details):
    registered=_warp(src,tgt,final_matrix,final_model)
    overlay=cv2.addWeighted(tgt,.5,registered,.5,0); difference=cv2.absdiff(tgt,registered)
    checker=np.where((np.indices(tgt.shape).sum(axis=0)//32)%2==0,tgt,registered).astype(np.uint8)
    kept=[m for m,ok in zip(best['matches'],best['geo'].inlier_mask) if ok]
    inliers=cv2.drawMatches(src,best['a'].keypoints,tgt,best['b'].keypoints,kept,None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    error_map=np.zeros((*src.shape[:2],3),np.uint8); confidence_map=np.zeros_like(error_map)
    for d in details:
        x,y=map(int,d['source_coordinate']); err=d['refined_error_px'] if d['refined_error_px'] is not None else d['reprojection_error_px']; val=min(255,int(255*min(err,20)/20)); cv2.circle(error_map,(x,y),5,(255-val,val,0),-1); c=d['confidence']; cv2.circle(confidence_map,(x,y),5,(int(255*c),int(255*(1-c)),0),-1)
    _,covdetail=coverage([d['source_coordinate'] for d in details],src.shape,grid=8); cells=np.array(covdetail['cells']); heat=cv2.resize(np.uint8(cells*(255/max(1,cells.max()))),(src.shape[1],src.shape[0]),interpolation=cv2.INTER_NEAREST); coverage_map=cv2.applyColorMap(heat,cv2.COLORMAP_VIRIDIS)
    images={'registered':registered,'overlay':overlay,'difference':difference,'checkerboard':checker,'inliers':inliers,'error_map':error_map,'coverage_map':coverage_map,'confidence_map':confidence_map}; paths={}
    for k,v in images.items(): path=out/f'{k}.png'; cv2.imwrite(str(path),v); paths[k]=str(path)
    return paths

def register(source,target,output_dir: str|Path,method='SIFT',repr_mode='auto',performance_mode='BALANCED',source_sensor='UNKNOWN',target_sensor='UNKNOWN',grid=8,source_band=None,target_band=None,representation_ensemble=True,multiscale=True,spatial_selection=True,subpixel_refinement=True,sun_source=None,sun_target=None,allow_homography=True,calibration=None):
    source,target=select_band(source,source_band),select_band(target,target_band)
    start=time.perf_counter(); run_id=uuid.uuid4().hex[:12]; out=Path(output_dir)/run_id; out.mkdir(parents=True,exist_ok=True)
    choice=choose_engine(performance_mode,source_sensor,target_sensor); method='ORB' if choice.active=='ORB' else method.upper()
    reps=[repr_mode] if repr_mode!='auto' else (['clahe','gradient','edge','local_contrast'] if representation_ensemble else ['raw'])
    factors=[1.0] if performance_mode.upper()=='FAST' or not multiscale else [.5,1.0]
    candidates=[_candidate(source,target,method,r,f,grid,spatial_selection,sun_source,sun_target) for r in reps for f in factors]
    best=max(candidates,key=lambda c:c['score'])
    src,tgt,geo=best['src'],best['tgt'],best['geo']
    initial_src=np.float32([best['a'].keypoints[m.queryIdx].pt for m,ok in zip(best['matches'],geo.inlier_mask) if ok]); initial_tgt=np.float32([best['b'].keypoints[m.trainIdx].pt for m,ok in zip(best['matches'],geo.inlier_mask) if ok])
    if subpixel_refinement and len(initial_src)>=3 and geo.model!='homography': refined,valid,lk_error=refine_lk(src,tgt,initial_src,initial_tgt)
    else: refined,valid,lk_error=initial_tgt.copy(),np.ones(len(initial_tgt),bool),np.full(len(initial_tgt),np.nan)
    final_matrix,final_model=geo.matrix,geo.model
    if geo.matrix is not None and valid.sum()>=3 and geo.model in ('similarity','affine'):
        estimated,_=cv2.estimateAffinePartial2D(initial_src[valid].reshape(-1,1,2),refined[valid].reshape(-1,1,2),method=cv2.RANSAC,ransacReprojThreshold=2)
        if estimated is not None:
            before=np.mean(np.linalg.norm(warp_points(initial_src[valid],geo.matrix,geo.model)-refined[valid],axis=1)); after=np.mean(np.linalg.norm(warp_points(initial_src[valid],estimated,'similarity')-refined[valid],axis=1))
            if after<=before: final_matrix=estimated; final_model='similarity'
    errors=reprojection_errors(best['a'].keypoints,best['b'].keypoints,best['matches'],final_matrix,final_model)
    points=[best['a'].keypoints[m.queryIdx].pt for m,ok in zip(best['matches'],geo.inlier_mask) if ok]
    metrics=summarize(errors,geo.inlier_mask,points,src.shape,time.perf_counter()-start,grid,final_model)
    metrics['initial_rmse_px']=float(np.sqrt(np.mean(best['errors'][geo.inlier_mask]**2))) if np.isfinite(best['errors'][geo.inlier_mask]).any() else None
    refined_residuals=np.linalg.norm(warp_points(initial_src,final_matrix,final_model)-refined,axis=1) if final_matrix is not None and len(refined) else np.array([])
    metrics['refined_rmse_px']=float(np.sqrt(np.mean(refined_residuals[valid]**2))) if valid.any() else None; metrics['subpixel_refined_matches']=int(valid.sum())
    quality,reason=quality_gate(metrics); status='SUCCESS' if quality in {'HIGH CONFIDENCE','MEDIUM CONFIDENCE'} else ('LOW_CONFIDENCE' if quality=='LOW CONFIDENCE' else 'INSUFFICIENT_FEATURES')
    details=[]; ii=0
    for match,inlier,error in zip(best['matches'],geo.inlier_mask,errors):
        if not inlier: continue
        kp=best['a'].keypoints[match.queryIdx]; rp=refined[ii] if ii<len(refined) else None; local=float(lk_error[ii]) if ii<len(lk_error) and np.isfinite(lk_error[ii]) else 99.; conf,cal=calibrated_confidence(match.distance,error,local,kp.response,calibration)
        details.append({'source_coordinate':[round(kp.pt[0],3),round(kp.pt[1],3)],'target_coordinate':[round(x,3) for x in best['b'].keypoints[match.trainIdx].pt],'refined_target_coordinate':[round(float(x),3) for x in rp] if rp is not None else None,'reprojection_error_px':round(float(error),4),'refined_error_px':round(float(refined_residuals[ii]),4) if ii<len(refined_residuals) else None,'confidence':conf,'confidence_calibrated':cal,'feature_type':terrain_type(kp),'scale':round(kp.size,3)}); ii+=1
    paths=_write_images(out,src,tgt,best,final_matrix,final_model,details)
    sunmeta={'source':illumination_descriptor(*(sun_source or (None,None))), 'target':illumination_descriptor(*(sun_target or (None,None)))}
    metadata={'source_sensor':source_sensor,'target_sensor':target_sensor,'source_band':source_band if source_band is not None else 'AUTO_STRUCTURAL','target_band':target_band if target_band is not None else 'AUTO_STRUCTURAL','engine':choice.__dict__,'representation_selected':best['rep'],'pyramid_levels_tested':factors,'match_count_before_spatial_filter':len(best['raw']),'match_count_after_spatial_filter':len(best['matches']),'transform_model':final_model,'quality_gate':quality,'quality_reason':reason,'sun_geometry':sunmeta,'local_processing':True,'ablation_flags':{'representation_ensemble':representation_ensemble,'multiscale':multiscale,'spatial_selection':spatial_selection,'subpixel_refinement':subpixel_refinement,'adaptive_geometry':True,'sun_geometry_correction':bool(sun_source or sun_target),'confidence_calibration':bool(calibration)}}
    paths['experiment_json']=str(out/'experiment.json'); (out/'experiment.json').write_text(json.dumps({'experiment_id':run_id,'metrics':metrics,'metadata':metadata,'correspondences':details},indent=2),encoding='utf-8')
    explanation=f"Selected {best['rep']} across pyramid levels. Spatial selection retained {len(best['matches'])} of {len(best['raw'])} candidates; {metrics['inliers']} survived {final_model} geometry. Quality gate: {quality} ({reason}). Sun geometry correction: {'enabled' if (sun_source or sun_target) else 'metadata unavailable'}. Residuals are internal consistency measurements, not absolute lunar ground-truth accuracy."
    return RegistrationResult(run_id,metrics,status,paths,explanation,metadata,details)
