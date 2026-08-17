import express from "express"
import { Router } from "express"
import {authMiddleware} from "../middleware/authMiddleware.js"

import { Login, Logout, Signup, Refresh, me } from "../controllers/authController.js";

const router = express.Router();

router.post("/login",Login);
router.post("/signup", Signup);
router.post("/logout", Logout);
router.post("/refresh", Refresh);
router.get("/me", authMiddleware, me);

export default router;
