import express from "express";

import {
    uploadDataset,
    getDatasets,
    getDatasetById,
    deleteDataset,
} from "../controllers/dataset.controller.js";

import { Protect } from "../middleware/auth.middleware.js";
import upload from "../middleware/upload.middleware.js";

const router = express.Router();

router.post(
    "/upload",
    Protect,
    upload.single("dataset"),
    uploadDataset
);

router.get(
    "/",
    Protect,
    getDatasets
);

router.get("/:datasetId",Protect,getDatasetById);

router.delete(
    "/:datasetId",
    Protect,
    deleteDataset
);

export default router;