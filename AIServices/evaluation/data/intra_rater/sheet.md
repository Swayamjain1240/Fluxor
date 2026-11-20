# Blind re-judgment sheet (L5)

Grade every passage: 2 = directly answers the query, 1 = supporting information, 0 = irrelevant to the query.

## Q07  query: How does stellar flare activity affect observations of exoplanet atmospheres?

### Q07-01  [D02 p15 230-670]
designed to detect transits of Earth-size planets in the “habitable zone” orbiting 9< mv<15, F through M type dwarf stars by means of differential photometry of >100,000 stars in the constellations Cygnus and Lyra. The photometric precision was expected to be 20 ppm for 12th magnitude G2V stars, for a 6.5 hr integration, though solar-type stars themselves turned out to be noisier than expected (Gilliland et al., 2011; Gilliland et

### Q07-02  [D03 p1 1867-2307]
; Covey et al. 2008) and frequently host rocky plan- ets at habitable zone (HZ) distances that could allow for stable liquid water on their surfaces (e.g. Dressing & Charbonneau 2013, 2015). However, the proximity of the HZ to the host star and frequent powerful ﬂares call into question the habitability of M-dwarf planets (Tarter et al. 2007). Flares occur when a star’s magnetic ﬁeld re-connects, releasing radiation across the electroma

### Q07-03  [D03 p6 3287-3727]
ence from the 20 second ﬂare peak reaching the surface of a habitable zone planet in the absence of a signiﬁcant atmosphere. Columns not shown but included in the machine-readable table include the ﬂare start and stop times in TBJD, the FWHM duration in minutes, the number of substructure peaks in the rise phase (Nrise), the number of peaks across the entire ﬂare (Ntot), the log of the quiescent luminosityQ0, and the estimated survival

### Q07-04  [D02 p94 1227-1302]
ace HGA High-gain antenna HST Hubble Space Telescope HZ Habitable Zone

### Q07-05  [D05 p2 1321-1761]
lved systems where the stellar light is the primary signal. Transmission spectroscopy is one such method, which works by taking the out-of-transit, disk- integrated spectrum of the host star and subtracting it from the spectrum taken as stellar flux passes through the planet atmosphere above the limb, ideally provid- ing an isolated spectrum of the planet’s atmosphere (S. Seager & D. D. Sasselov 2000; T. M. Brown 2001). The multi-wavele

## Q12  query: What morphology classes are used to describe eclipsing binary light curves?

### Q12-01  [D06 p2 1113-1553]
the widely used discrete classes, we propose a binary star morphology classiﬁcation based on a dimensionality reduction algorithm. Finally, we present statistical properties of the sample, we qualitatively estimate completeness, and discuss the results. The work presented here is organized and performed within the TESS Eclipsing Binary Working Group, an open group of professional and citizen scientists; we conclude by describing ongoin

### Q12-02  [D06 p4 889-1329]
al detection algorithm with minimal requirements for signal morphology. The merit function (ζ) of a given trial period (Ptrial) is calculated using (I) local decrease inχ2 of the binned, phase-folded light curve and (II) the kurtosis characterizing the tailedness of the binned ﬂux distribution to ensure a mostly ﬂat baseline with one (or a few) excursion(s) representing a dimming event. Chakraborty et al. (2020) applied the algorithm to

### Q12-03  [D03 p2 3916-4356]
statistical sam- ple of ﬂares. In Section 4, we explore the morphology of our sample of 20 second cadence ﬂare sample. In Section 5, we describe quasi-periodicity in the substructure of the ﬂares. In Section 6, we describe common morphologies among complex ﬂares. In Section 7, we explore habit- ability implications of 20 sec cadence ﬂare emission. In Section 8, we summarize and conclude. 2. TESS OBSERVATIONS In its initial and extended

### Q12-04  [D03 p1 4704-5144]
al. 2016; Howardetal.2020b). Theimpulseofaﬂaredescribesthe morphology of the ﬂare light curve and is deﬁned as the amplitude of a ﬂare’s peak in fractional-ﬂux units over its FWHM duration in minutes (Kowalski et al. 2013). Because highly impulsive superﬂares deliver the same amountofUVﬂuxmuchmorerapidlythanlessimpulsive ones, it is likely the temporal structure of the ﬂare peak could inﬂuence the rates of key reactions in atmospheric

### Q12-05  [D07 p8 731-1851]
and Kepler data. In Figure 4, we show a scatter plot of the morphology parameter vs. T mag of the Kepler EBs found (blue) and not found (red) by our neural network. The morphology parameter (described further in Prˇ sa et al. 2011) is a measure of the EB type, with values less than 0.5 corresponding to detached EBs, values in the range 0.5-0.7 being semi-detached EBs, 0.7-0.8 being overcontact EBs, and greater than 0.8 corresponding to ellipsoidal or unknown classifications. We exclude analysis where the morphology parameter was given a value of -1, indicating the lightcurve was unclassifiable by the methods of Prˇ sa et al. 2011. Furthermore, we make the same comparison using the EB period vs. T mag in Figure 5 and EB period vs. morphology parameter in Figure 6. We can make two conclusions from these figures: (i) The T mag histograms in the left panels ( Kepler comparisons) of Figures 4 and 5 show a clear decrease in performance with decreasing T mag, while we do not see the same decrease in the right panels ( TESS comparisons) of the same figures. Although there is a somewhat artificial lower limit on

## Q17  query: How is a periodic variability signal searched for in a light curve?

### Q17-01  [D04 p11 3484-4215]
rotation period, we used both the Generalized Lomb- Scargle periodogram (GLS) (Zechmeister & K¨ urster 2009) from the Python package astropy.timeseries (Astropy Collaboration et al. 2013) and the Autocorrelation Function (ACF) to estimate this parameter for every star. We selected the highest peak with a false alarm probability lower than 1% in the periodogram as the LS rotation period of the star. We then produced the phase curve by folding the raw light curve with this period and examined the validity of the period by fitting the binned phase curve with a 5th-order Fourier series function, estimating the R-square value between the best-fit model and the binned phase curve. We employed the ACF to further validate the per

### Q17-02  [D04 p18 4588-5198]
20,000 stars, determined using the Generalized Lomb-Scargle periodogram and the Autocorrelation Function (ACF), as implemented in the astropy.timeseries package. Valid rota- tion periods were identified by the highest peak in the periodogram with a false alarm probability below 1%, further confirmed by an R-square value exceeding 0.7 after fitting a 5th-order Fourier series to the phase curve. Consistency within 5% between the Lomb-Scargle and ACF methods was required for a period to be accepted. Due to the limitations of our light curve detrending approach, our analysis excluded known eclipsing binarie

### Q17-03  [D06 p5 916-1592]
o searching for transit-like signals: the Box Least Squares Periodogram (BLS; Kov´ acs et al. 2002). In the BLS periodogram, a sliding box-like signal is passed over the light curve for a range of orbital periods, and the likelihood of the model is recorded at each orbital period. The resulting periodogram is expected to peak at integer multiples of the any box-like periodic signals in the light curve, and thus is well-suited to the detection of eclipses. We used the BLS implementation in Astropy (Astropy Collaboration et al. 2013) with the lightkurve package (Barentsen et al. 2019) to normalize and prepare the light curves. No further pre-processing was applied to th

### Q17-04  [D03 p9 590-1247]
d error measurement process. A Bayesian log-likelihood ﬂare periodogram is computed and the highest peak consistent with the substructure component inter-arrival times is selected. Period errors are measured as the FWHM of the selected peak. Each peak is also conﬁrmed with LS periodograms of the light curve variability from the middle panel. Figure 7. Two examples of candidate QPPs showing evidence of period evolution. Substructure in the left ﬂare is consistent with a period of 7.32 min in the rise phase, but a slightly longer period of 9.34 min during the decay phase. The “period" in the right ﬂare constantly increases from 4.13 min up to∼22 min.

### Q17-05  [D03 p8 2889-3329]
most likely period and period er- rors with a Bayesian ﬂare periodogram developed in Howard & Law (2021) to determine periodic- ity in a discrete set of events in noisy and incom- plete data. The log-likelihood of a given period- icity P on a set of event times Fi, logL(P|Fi), is determined using Baye’s theorem and a proba- bility comb Prob(Fi|Pcomb) that allows for slight imperfections in the arrival times of each event as described in

## Q19  query: How is the completeness of a variability catalogue estimated?

### Q19-01  [D05 p9 262-702]
by ED to reduce the effects of low-energy flare detection incompleteness. A two-component Gaussian Mixture Model (GMM) separates the stars into two clusters: lower activity (blue) and highly active (gold).Right panel:Full flare frequency distributions (FFDs) for each star, colored by their GMM-assigned label. Figure 3.Flare frequency distributions for all M dwarf targets from detected flares in their SPOC light curves. In both panels, t

### Q19-02  [D05 p8 3632-4072]
is still debated and seemingly limited by flare de- tection completeness. Studies of optical flare frequency distributions across stars of all spectral types have found some variation in calculated power law exponents,α (also commonly referred to as the power law index or slope), but it is typically aroundα≈2 (C. H. Lacy et al. 1976; N. I. Shakhovskaia 1989; E. J. Hilton 2011; T. Shibayama et al. 2013; S. L. Hawley et al. 2014; J. C. Lu

### Q19-03  [D01 p65 332-772]
hat the SDPDD may be updated as the mission progresses. For completeness, historical Data Anomaly ﬂags will also be documented here (see§A.2.3). A.2.1 Summary Bits 1, 2, 3, 4, and 6 (Attitude Tweak, Safe Mode, Coarse Point, Earth Point, and Reaction Wheel Desaturation Event) are assigned to cadences based on spacecraft telemetry. Bits 5, 7, 9, 10, and 11 (Argabrightening events, Cosmic Ray in Aperture, Discontinuity, Impulse Outlier, an

### Q19-04  [D04 p15 965-1405]
power-law slope is challenging due to issues with detection completeness. The frequency distribution at lower energies is often incomplete, affected by limitations such as the sampling interval and the photometric precision of the survey. To address these uncertainties at lower energy levels, we conducted an injection and recovery test before calculating the power-law slope index. We employed Equations 1 to 4 from Gryciuk et al. (2017)

### Q19-05  [D04 p16 19-459]
calculations not accounting for uncertainties due to the incompleteness of small flares. By fitting the cumulative flare frequency distribution starting from log(Ef) = 35.6, similar to the initial energy used by (Yang et al. 2023, their Figure 19), and excluding smaller flares, we obtained an α of 2.23± 0.24, which aligns closely with their results. For A-dwarfs’ flares, Yang & Liu (2019) reported a power-law slope α of 1.12± 0.08. Sim

## Q26  query: How are supernova candidates reported and followed up?

### Q26-01  [D12 p2 63-503]
curve classiﬁcation of 8.5× 105 objects, the report of 3088 supernova candidates, and diﬀerent experiments using LSST-like alert streams. Finally, we discuss the challenges ahead to go from a single-stream of alerts such as ZTF to a multi–stream ecosystem dominated by LSST. Keywords: editorials, notices — miscellaneous — catalogs — surveys 1. INTRODUCTION The exponential growth of the light collecting area of telescopes and the number o

### Q26-02  [D08 p1 1726-2502]
nt to capture non-transit astrophysical variations, such as supernova signals or stellar variability, that tend to be removed in techniques optimized for exoplanet detection. We validate our method by de-trending diﬀerent sources (e.g., supernova, tidal disruption event (TDE), exoplanet-hosting star, fast-rotating star) and comparing our light curves to those obtained by other pipelines when appropriate. Our supernova and TDE light curves are visually similar to those obtained by others using the ISIS image subtraction package, indicating that unpopular can be used to extract multi-sector light curves by preserving astrophysical signals on timescales of Corresponding author: Soichiro Hattori soichiro.hattori@columbia.edu arXiv:2106.15063v2 [astro-ph.IM] 5 Apr 2022

### Q26-03  [D08 p2 2226-2886]
nvestigations on a variety of astronomical phenomena (e.g., supernovae, asteroids, ﬂaring stars, eclipsing binaries, tidal disruption events, variable stars, mi- crolensing events). Some examples include studying the early-time behavior of tran- sient events, such as the Type-Ia supernova ASASSN-18tb/SN 2018fhw (Vallely et al. 2019) and the tidal disruption event ASASSN-19bt/AT 2019ahk (Holoien et al. 2019). The FFI data has also shown promising potential for detecting distant Solar System objects (Holman et al. 2019; Payne et al. 2019), where Rice & Laughlin (2020) were recently able to successfully recover the signals of three trans-Neptunian objects

### Q26-04  [D11 p2 46-486]
tive – methods: data analysis – stars: variables: general – supernovae: general – surveys 1. INTRODUCTION Brightness variations of astrophysical objects oﬀer key insights into their physical emission mechanisms and related phenomena. In stars, pulsations, both radial and non-radial, can result from a thermodynamic en- gine operating in their partial ionization layers, when stars are located inside one of the several so-called in- stabil

### Q26-05  [D11 p3 3096-3536]
Lensing Experiment (OGLE; Udalski et al. 1992) and the Open Supernova Catalog (OSC; Guillo- chon et al. 2017) to classify seven transient and variable star classes; and D’Isanto et al. (2016) used Catalina Real-Time Transient Survey (CRTS; Drake et al. 2009) data to classify six transient and variable object classes. Other works have tested techniques to classify diﬀerent classes of variables and transients using synthetic data (e.g., B

## Q36  query: What is a causal pixel model and how is it fitted?

### Q36-01  [D08 p5 2202-2642]
ss certain aspects of the method and summarize our work. 2. CAUSAL PIXEL MODEL In this section we describe the concepts behind the CPM (and its variant CPM Diﬀerence Imaging ) method and discuss the modiﬁcations we have made in our unpopular implementation. As mentioned in §1, CPM is within the family of meth- ods that attempts to model the systematics as a combination of some chosen set of regressors (e.g., Smith et al. 2012; Stumpe et

## Q37  query: How is photometric precision characterised for a transit survey?

### Q37-01  [D06 p14 1545-2316]
eness qualitatively, we start with the Combined Diﬀerential Photometric Precision (CDPP; Gilliland et al. 2011). CDPP is a measure of light curve variation – the rms noise of the result of ﬁltering the timeseries with a high-pass Savitzky-Golay ﬁlter and then applying a moving average of 0.5-hr. The top panel in Fig. 12 shows CDPP as a function of magnitude for Sector 1 observations. The CDPP values are inherent to aperture light, so they are not corrected for crowding. The second panel in Fig. 12 provides a statistical estimate of per-target crowding, i.e., the fraction of light in the aperture coming from the target itself. Thus, a value of 1 means that all light is due to the observed target, while a value of, say, 0.6, means that 60% of the light comes from

### Q37-02  [D08 p18 2931-3040]
rs, we calculated a proxy for the 6-hr combined diﬀerential photometric precision (CDPP) (Christiansen et al.

### Q37-03  [D01 p54 44-762]
of 6 December 2018) Figure 8.2: 1-hour Combined Diﬀerential Photometric Precision (CDPP). The red points are the RMS CDPP measurements for the 15,889 light curves from Sector 1 plotted as a function of TESS magnitude. The blue x’s are the uncertainties, scaled to 1-hour timescale. The purple curve is a moving 10th percentile of the RMS CDPP measurements, and the gold curve is a moving median of the 1-hr uncertainties. 9.1.1 Ground Contacts The spacecraft is in contact with the ground multiple times per orbit. High-data-rate downlinks of the accumulated science data from the previous orbit occur during LAHO. Three low-data-rate contacts during HASO are used for ranging to the spacecraft and to check observator

### Q37-04  [D06 p16 0-1068]
16 Prˇsa et al. Magnitude 102 103 104 105 106 0.5-hour CDPP [ppm] Magnitude 0.0 0.2 0.4 0.6 0.8 1.0Crowding Magnitude 103 105 107 Corrected CDPP 2 4 6 8 10 12 14 16 18 Magnitude 1.0 1.5 2.0 2.5 3.0Flattened CDPP Figure 12. The TESS Combined Diﬀerential Photometric Precision (CDPP). The top panel depicts the measured CDPP with a 0.5-hr running average, in ppm. The second panel provides a crowding measure per target, i.e., the fraction of light in the aperture from the observed target. The third panel corrects the original CDPP for crowding: corrected CDPP = CDPP / crowding. This assumes that the contribution of background light does not vary with time, which may or may not be true. Depicted in blue are all observed targets, and in red are the EBs. The bottom panel is the ﬂattened version of the previous panel, divided by the bottom envelope. the trend of all targets observed in Sector 1 – as we see no systematic features in the ﬂattened CDPP, we conclude that the number distribution is a fair reﬂection of the true CDPP distribution for the observed EBs.

### Q37-05  [D02 p86 3175-3638]
ense the total noise, referred to as combined differential photometric precision (CDPP) is: € P=P0 2+σ* 2 Eq. 7.5-3 For brighter sources the precision will be better than that of a 12th magnitude star, but the simple formula above will be inaccurate as bright star photometry is dominated by systematic effects rather than just shot

## Q49  query: How are light curves from different observing sectors combined?

### Q49-01  [D04 p3 881-1695]
ras, with the pixel scale of 21 ′′× 21′′, of TESS provide a combined field of view of 24 o× 96o, effectively covering the sky in two hemispheres divided into 13 sectors each. Each sector represents a block within the TESS field of view, with each block being observed for approximately 27 days. TESS sequentially observes these blocks, moving from one to the next, until it covers all sectors. By January, 2024, TESS have observed 72 sectors covering about 85% of the sky and accumulating approximately 1.3 million short-cadence light curves from over 490,000 sources. In this section, we illustrate the approaches to pre-processing the TESS short cadence light curves and display how we collect true and false flare samples to train the machine learning models. To carry out our study, we utilized the Python pack

### Q49-02  [D06 p14 1524-2289]
. To estimate completeness qualitatively, we start with the Combined Diﬀerential Photometric Precision (CDPP; Gilliland et al. 2011). CDPP is a measure of light curve variation – the rms noise of the result of ﬁltering the timeseries with a high-pass Savitzky-Golay ﬁlter and then applying a moving average of 0.5-hr. The top panel in Fig. 12 shows CDPP as a function of magnitude for Sector 1 observations. The CDPP values are inherent to aperture light, so they are not corrected for crowding. The second panel in Fig. 12 provides a statistical estimate of per-target crowding, i.e., the fraction of light in the aperture coming from the target itself. Thus, a value of 1 means that all light is due to the observed target, while a value of, say, 0.6, means that

### Q49-03  [D01 p11 1611-2051]
ll have been distributed with the ﬁrst release of data from Sectors 1 and 2. While the document is relatively complete, there are sections that will be expanded, and there are analyses in progress that will contribute to the details of the document. In addition, the Instrument Handbook will be regularly updated to incorporate results of analyses of on-orbit data. Revisions to the TIH may be made on a∼monthly basis during the ﬁrst year o

### Q49-04  [D06 p3 4137-4969]
he next light curve. Once all of the data from a given TESS sector have been classiﬁed, the classiﬁcations from the individual volunteers are combined using an unsupervised machine learning algorithm. This allows us to identify times of potential transit-like events in each light curve and rank all of the candidates from most to least likely to contain a transit signal (for details see Eisner et al. 2021). The 500-700 highest ranked candidates per sector are visually inspected by the PHT science team and grouped into ‘planet candidates’, ‘EB candidates’ and ‘other’. In total, we identiﬁed 2720 EB candidates using this methodology. In addition to this classiﬁcation pipeline, each target has an independent discussion forum, where the citizen scientists can discuss the data, and ﬂag the signals to the science team using sea

### Q49-05  [D01 p54 23-592]
k Version 0.1 (Draft of 6 December 2018) Figure 8.2: 1-hour Combined Diﬀerential Photometric Precision (CDPP). The red points are the RMS CDPP measurements for the 15,889 light curves from Sector 1 plotted as a function of TESS magnitude. The blue x’s are the uncertainties, scaled to 1-hour timescale. The purple curve is a moving 10th percentile of the RMS CDPP measurements, and the gold curve is a moving median of the 1-hr uncertainties. 9.1.1 Ground Contacts The spacecraft is in contact with the ground multiple times per orbit. High-data-rate downlinks of the a

## Q52  query: What is the pixel scale and field of view of the TESS cameras?

### Q52-01  [D01 p11 806-1246]
details of the data processing pipeline. describing how raw pixel data are transformed into photometric time series, the theoretical basis of the algorithms used to reduce data, and a description of residual instrument artifacts after Pipeline processing. 1.2 Document Organization The Handbook begins with an overview of the TESS mission, instrument, spacecraft, and orbit. The optical and detector assemblies are described in detail in §3

### Q52-02  [D02 p29 201-1005]
ter, a 1.4 m diameter primary mirror, and a 16.1° diameter field of view – a sky area equivalent to 5 Palomar Schmidt plates. The photometer wavelength range is 420-900 nm, as shown in detail in §3.3. The resulting f/# for the system is 1.473 on-axis with an effective focal length of 1399.20 mm. The telescope illuminates forty- two 1044 x 2200 science CCDs and four 512 x 512 FGS CCDs made up of 27µm pixels and 13µm pixels respectively. These flat CCDs are matched to the curved focal surface using field flattener lenses (FFLs) and the mechanical arrangement discussed in §4.2. The rotation, translation, and defocus of each as- built CCD with respect to the design value is given in KEPLER.SER.FPA.021. There are 3 focusing mechanisms attached to the primary mirror. Figure 10: Kepler

### Q52-03  [D01 p13 1273-1761]
MIT/LL CCID-80 CCDs per Camera 4 CCD Dimensions 2048× 2048 pixels in imaging array Pixel Size 15 µm square Pixel Depth 100 µm Lens Custom 146 mm, f/1.4 lens (MIT/LL Design) Bandpass 600-1040 nm Camera Temperature −85◦C (lens),−80◦C (CCDs) 2.3.1 TESS Cameras The TESS camera consists of a detector assembly, a lens assembly, and a lens hood (Figure 2.2). The detector assembly houses the focal plane electronics and the focal plane array. The focal plane array consist of four large-forma

### Q52-04  [D02 p4 1340-1780]
-time models (KAM §2.3.5.14 and §2.3.5.15), converts sky to pixel coordinates (Section 7.6). 16 3.10 Replace "Quantitative discussion of ghosts and stray light will added to the next version of this document" with "Stray light was measured during Photometer testing and the first year of flight (Caldwell et al., 2010). " 17 4.3 Add some FGS info to table 7 18 4.5 Charge injection "2%" to "40% full-well" 19 4.7 Change "Read nois

### Q52-05  [D04 p3 835-1483]
table for stellar flare studies. The four cameras, with the pixel scale of 21 ′′× 21′′, of TESS provide a combined field of view of 24 o× 96o, effectively covering the sky in two hemispheres divided into 13 sectors each. Each sector represents a block within the TESS field of view, with each block being observed for approximately 27 days. TESS sequentially observes these blocks, moving from one to the next, until it covers all sectors. By January, 2024, TESS have observed 72 sectors covering about 85% of the sky and accumulating approximately 1.3 million short-cadence light curves from over 490,000 sources. In this section, we illustrate th

## Q56  query: What is the difference between full-frame images and target pixel files?

### Q56-01  [D01 p17 1321-2141]
ls; brighter stars will be given larger stamps. The list of target pixels is then uplinked to the DHU. During science observations, the DHU uses data from 60 consecutive two-second integrations to create two-minute postage stamps from the uplinked target pixel list. Cosmic-ray mitigation (see§5.1) is applied to these stacks, which reduces the eﬀective exposure time to 96 seconds. The postage-stamp data are calibrated and formatted into target pixel FITS ﬁles in a format modeled on the Kepler format. 2.6.2 Full-Frame Images The high data downlink capability allows FFIs to play a signiﬁcant scientiﬁc role for TESS. During science operations, the DHU continuously uses data from 900 consecutive two-second images to create 30-minute FFIs for all cameras. Cosmic-ray mitigation is applied to the FFIs, which reduces

### Q56-02  [D02 p69 1021-1461]
ource at nontarget source pixel smorc which couples to the target pixel sm’o’rc. Empirically, intramodule crosstalk -- the coupling between the different outputs of a given module (m = m’,o ≠ o’) -- is significant, while the intermodule crosstalk (m ≠ m’) is not. This is not surprising, since the LDE was designed with shields between the board pairs and staggered module read-out (time slice) to eliminate intermodule crosstalk, bu

### Q56-03  [D10 p3 1351-1916]
our source. Here, nearby means contribut- ing light to the target pixel ﬁles (TPFs) that are read out around every short-cadence target, or to the sub- frame cutouts acquired from the full frame images with TESSCut (Brasseur et al. 2019). For simplicity, we will refer to both as TPFs in this work. Putting this as- sumption another way, the only appreciable eﬀect that other stars have on the periodograms of light curves ex- tracted from a TPF is on the measurement noise at the frequencies speciﬁed. This assumption will be satisﬁed in most cases, owing to the

### Q56-04  [D02 p42 60-500]
4. Detector Properties 4.1 CCD Architecture The CCDs are full frame, thinned, back illuminated, anti-reflection coated, 4-phase, dual output, 2200x1044 pixel line-transfer devices. A readout amplifier is located on both ends of the serial register and during normal operation one half of each science CCD is read out by a single output, as shown in Figure 19. The 20 rows closest to the serial register are masked with an opaque light

### Q56-05  [D01 p52 1719-2159]
2.5 days: these are quite evident in the science data, both target pixels and FFIs. A modiﬁed ACS algorithm that does not use momentum wheel speed measurements was developed, and initial testing was performed during Orbit 13 (Sector 3). The jitter performance was seen to be signiﬁcantly better. Momentum dumps every 3.0 days are used to keep the momentum wheels in a quieter range; analyses are in progress to help assess whether the time

## Q57  query: How does TESS select which stars to observe at two-minute cadence?

### Q57-01  [D03 p1 556-996]
sed energies of≥1033 erg. We discover degeneracy present at 2 minute cadence between sharply-peaked and weakly-peaked ﬂares is common, although 20 second cadence breaks these degeneracies. We better resolve the rise phases and ﬁnd 46% of large ﬂares exhibit substructure during the rise phase. We observe 49 candidate quasi-periodic pulsations (QPP) and conﬁrm 17 at≥3σ. Most of our QPPs have periods less than 10 minutes, suggesting short

### Q57-02  [D03 p2 2792-3232]
et al. 2021; Pope et al. 2021; Howard & Law 2021). However, 2 minute cadence TESS observations do not consistently resolve the substructure of these ﬂares. Beginning in Cycle 3, a new 20 second cadence mode was introduced as part of TESS’s extended mission. The new TESS 20 sec- ond cadence mode has already shown great promise in resolving short-period asteroseismic oscillations (Huber et al. 2021) and stellar ﬂares from AU Mic (Gilbert

### Q57-03  [D01 p17 250-1333]
hich sums them on the ﬂy to create two basic data products: two-minute stacked subarrays and 30-minute FFIs. The two-minute subarrays are centered on stars with the potential for exoplanet discovery, asteroseismology targets, and calibration sources, while the FFIs can be examined for transiting planets around targets not speciﬁed in the two-minute data set, along with a wide variety of other astrophysical phenomena. These data products are compressed, stored on board, and downlinked to the ground at every perigee pass. These data products, along with ancillary engineering data, are described in detail in the Science Data Products Description Document. 2.6.1 Two-minute “postage stamp” Data The two-minute postage stamps are similar to the long- and short-cadence data collected by Kepler. During mission observation planning, targets for postage-stamp data are selected (cf. §9.4), and the pixels associated with each of these targets are identiﬁed. For the majority of targets, an 11× 11 pixel box is suﬃcient to enclose the optimum aperture and background pixels; brighter

### Q57-04  [D04 p1 850-1290]
CT We apply multi-algorithm machine learning models to TESS 2-minute survey data from Sectors 1-72 to identify stellar flares. Models trained with Deep Neural Network, Random Forest, and XG- Boost algorithms, respectively, utilized four flare light curve characteristics as input features. Model performance is evaluated using accuracy, precision, recall, and F1-score metrics, all exceeding 94%. Validation against previously reported TESS

### Q57-05  [D01 p29 1681-2121]
ected pixels 60 deep, with cosmic-ray mitigation, to create two-minute cadence data. The Proton400k takes data of each type, compresses them, and stores them in the SSR prior to encapsulation as CCSDS packets for the Ka-band transmitter. 5.1 Cosmic-Ray Mitigation Cosmic-ray hits on the TESS CCDs have been assessed to be a signiﬁcant source of excess noise unless mitigated. This is especially true for FFIs, where nearly half of the pixel

## Q58  query: What limits the photometric sensitivity for faint targets?

### Q58-01  [D08 p13 945-1553]
ial transit signal. These choices were made to increase the sensitivity to faint transits that could be potential Earth analogs. As the detection of faint transits is not a priority for unpopular we do not require this level of sensitivity. We therefore setk∼100−200 for a single-sector (∼27 day) TESS light curve to signiﬁcantly increase the eﬃciency and do not exclude any neighboring ﬂux measurements. We allow the user to specify the number of sections and discuss the eﬀect of changing this tuning parameter in §3.5. 3. CREATING DE-TRENDED TESS LIGHT CURVES WITH UNPOPULAR In this section we describe th

### Q58-02  [D02 p36 1504-1944]
st pixel can actually degrade the photometry by increasing sensitivity to image motion, and degrade DIA (Differential Image Analysis) by degrading centroid accuracy. On the other hand, the SNR is decreased by making the PRF too broad, since a sum over more zodiacal light, background stars (and their noise), and pixels (with their read noise) will be needed to capture the flux. This noise increase is significant since, on average,

### Q58-03  [D01 p22 384-824]
close to 100 µm. This deep depletion depth enhances the red sensitivity of the CCD, but also increases the volume sensitive to cosmic-ray interactions. Figure 4.1 shows the overall architecture of the CCID-80. Figure 4.1: CCID-80 architecture The imaging array for the CCID-80 is comprised of 2048(H) ×2048(V) pixels. The active imaging array is surrounded by 10 extra rows and columns each on the left, right, top, and bottom sides to buﬀe

### Q58-04  [D01 p26 673-1241]
ﬂight-like CCID-80 show the overall CCD QE and the thermal sensitivity of the QE at the red end of the spectrum. Right: The absorption length of silicon at four temperatures, showing the sensitivity to temperature at the red end of the spectrum. the frame-store regions of the four CCDs, revealing only the imaging arrays of the FPA (Figure 4.6, right). Each CCD and its associated ampliﬁer circuitry is bonded to a SiC pedestal. The four pedestals are then mounted onto a monolithic SiC focal plane. The ﬂatness of the FPA can be adjusted with shims under the pedest

### Q58-05  [D02 p57 331-771]
this also explains the relative unimportance of intrapixel sensitivity variations for short-wavelength light, which is absorbed above the active region and must diffuse down into it prior to readout. The “blue” light never sees the gate structure, which has the opportunity to scatter the “red” light. Like chromatic aberration, the wavelength dependence of intrapixel response gives a PRF which varies with wavelength, and hence with
