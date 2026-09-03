import cookieParser from "cookie-parser";
import express from "express"
import dotenv from "dotenv";
dotenv.config();
import dns from "dns"
dns.setServers(["1.1.1.1","8.8.8.8"]);
import { connectDB } from "./utils/db.js";

import authRouter from "./routes/authRoute.js"
import authRoutes from "./routes/auth.routes.js";
import datasetRoutes from "./routes/dataset.routes.js";
import anomalyRoutes from "./routes/anomaly.routes.js";
import investigationRoutes from "./routes/investigation.routes.js";
import reportRoutes from "./routes/report.routes.js";
import validationRoutes from "./routes/validation.routes.js";
import dashboardRoutes from "./routes/dashboard.routes.js";

const app = express()

const PORT = process.env.PORT;
app.use(express.json());
app.use(cookieParser());

app.get("/api/health", (req,res)=>{
    res.status(200).json({success: true,message: "Fluxor backend is running",});
});

app.use("/api/auth", authRouter);
app.use("/api/auth", authRoutes);

app.use("/api/datasets", datasetRoutes);

app.use("/api/anomalies", anomalyRoutes);

app.use("/api/investigations", investigationRoutes);

app.use("/api/reports", reportRoutes);

app.use("/api/validations", validationRoutes);

app.use("/api/dashboard", dashboardRoutes);


app.listen(PORT,()=>{
    connectDB()
    console.log("server is running..");
})