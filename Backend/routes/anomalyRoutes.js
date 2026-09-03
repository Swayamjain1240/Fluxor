import express from "express";

import {
    detectAnomalies,
    getCandidates,
    getCandidateById,
    getCandidateLightCurve,
} from "../controllers/anomaly.controller.js";

import {Protect} from "../middleware/auth.middleware.js";

const router = express.Router();

router.post(
    "/datasets/:datasetId/detect",
    Protect,
    detectAnomalies
);

router.get(
    "/",
    Protect,
    getCandidates
);

router.get(
    "/:candidateId",
    Protect,
    getCandidateById
);

router.get(
    "/:candidateId/lightcurve",
    Protect,
    getCandidateLightCurve
);

export default router;