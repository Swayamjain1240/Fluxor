import express from "express";

import {
    startInvestigation,
    getInvestigations,
    getInvestigationById,
    getInvestigationStatus,
} from "../controllers/investigation.controller.js";

import { Protect } from "../middleware/auth.middleware.js";

const router = express.Router();

router.post(
    "/:candidateId/analyze",
    Protect,
    startInvestigation
);

router.get(
    "/",
    Protect,
    getInvestigations
);

router.get(
    "/:investigationId",
    Protect,
    getInvestigationById
);

router.get(
    "/:investigationId/status",
    Protect,
    getInvestigationStatus
);

export default router;