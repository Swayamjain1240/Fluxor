import numpy as np

FEATURE_NAMES = [
    "mean_flux",
    "std_flux",
    "median_flux",
    "amplitude",
    "iqr",
    "mad",
    "slope",
    "outlier_ratio",
]

def calculate_features(time,flux):
    mean_flux = np.mean(flux)

    std_flux = np.std(flux)

    median_flux = np.median(flux)

    amplitude = (np.max(flux) - np.min(flux))

    q25, q75 = np.percentile(flux,[25, 75])

    iqr = q75 - q25

    mad = np.median(
        np.abs(
            flux - median_flux
        )
    )

    shifted_time = (
        time - np.mean(time)
    )

    if np.ptp(shifted_time) == 0:

        slope = 0.0

    else:

        slope = np.polyfit(
            shifted_time,
            flux,
            1
        )[0]


    if mad > 0:

        deviation = np.abs(
            flux - median_flux
        )

        outlier_ratio = np.mean(
            deviation > (3 * mad)
        )

    else:

        outlier_ratio = 0.0


    return [
        float(mean_flux),
        float(std_flux),
        float(median_flux),
        float(amplitude),
        float(iqr),
        float(mad),
        float(slope),
        float(outlier_ratio),
    ]

def extract_window_features(
    time,
    flux,
    window_size=200,
    step_size=100,
    min_points=80
):

    feature_vectors = []

    windows = []


    start = 0

    window_id = 0


    while start < len(flux):

        end = min(
            start + window_size,
            len(flux)
        )


        window_time = time[start:end]

        window_flux = flux[start:end]


        if len(window_flux) >= min_points:

            features = calculate_features(
                window_time,
                window_flux
            )


            feature_vectors.append(
                features
            )


            windows.append({
                "windowId":
                    window_id,

                "startIndex":
                    start,

                "endIndex":
                    end,

                "startTime":
                    float(window_time[0]),

                "endTime":
                    float(window_time[-1]),
            })


            window_id += 1


        start += step_size


    if len(feature_vectors) < 5:

        raise ValueError(
            "Not enough windows for anomaly detection"
        )


    return (
        np.asarray(
            feature_vectors,
            dtype=float
        ),
        windows
    )