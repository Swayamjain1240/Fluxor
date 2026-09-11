import express from "express";

import {
    createDataset,
    getDatasets,
    getDatasetById,
    deleteDataset,
} from "../controllers/datasetController.js";

import { Protect  } from "../middleware/authMiddleware.js";

const router = express.Router();

router.post(
    "/",
    Protect ,
    createDataset
);

router.get(
    "/",
    Protect ,
    getDatasets
);

router.get(
    "/:datasetId",
    Protect ,
    getDatasetById
);

router.delete(
    "/:datasetId",
    Protect ,
    deleteDataset
);

export default router;