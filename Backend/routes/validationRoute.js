import express from "express";

import {
    createValidation,
    getValidations,
    getValidationById,
} from "../controllers/validation.controller.js";

import { Protect } from "../middleware/auth.middleware.js";

const router = express.Router();

router.post(
    "/",
    Protect,
    createValidation
);

router.get(
    "/",
    Protect,
    getValidations
);

router.get(
    "/:validationId",
    Protect,
    getValidationById
);

export default router;