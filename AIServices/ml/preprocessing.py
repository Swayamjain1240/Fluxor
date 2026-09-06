import numpy as np 

def preprocess_light_curve(time, flux):
    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)

    if len(time) != len(flux):
        raise ValueError(
            "Time and flux arrays must have equal length"
        )

    if len(time) < 100 :
        raise ValueError(
            "Not enough light curve points"
        )

    valid_mask = (np.isfinite(time) & np.isfinite(flux))

    time = time[valid_mask]
    flux = flux[valid_mask]

    if len(time) < 100 :
        raise ValueError(
           "Not enough valid data after cleaning"  
        )
    
    order = np.argsort(time)
    time = time[order]
    flux = flux[order]

    median_flux = np.median(flux)
    if median_flux == 0:
        raise ValueError(
            "Cannot normalize light curve with zero median"
        )

    normalized_flux = (
        flux / median_flux
    )


    return time, normalized_flux