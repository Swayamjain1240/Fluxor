import express from "express";

import {
    createDataset,
    getDatasets,
    getDatasetById,
    deleteDataset,
} from "../controllers/dataset.controller.js";

import { Protect  } from "../middleware/auth.middleware.js";

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