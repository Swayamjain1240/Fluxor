import cookieParser from "cookie-parser";
import express from "express"
import dotenv from "dotenv";
import cors from "cors"
dotenv.config();
import dns from "dns"
dns.setServers(["1.1.1.1","8.8.8.8"]);
import { connectDB } from "./utils/db.js";

import authRouter from "./routes/authRoute.js"
import datasetRoutes from "./routes/datasetRoutes.js";
import anomalyRoutes from "./routes/anomalyRoutes.js";
import investigationRoutes from "./routes/investigationRoutes.js";
import reportRoutes from "./routes/reportRoute.js";
import validationRoutes from "./routes/validationRoute.js";
import dashboardRoutes from "./routes/dashboardRoute.js";

const app = express()
// app.use(
//     cors({
//         origin: "http://localhost:5173",
//         credentials: true,
//     })
// );
const PORT = process.env.PORT;

app.use(express.json());
app.use(
    express.urlencoded({
        extended: true,
    })
);
app.use(cookieParser());

app.get("/api/health", (req,res)=>{
    return res.status(200).json({success: true,message: "Fluxor backend is running",});
});

app.use("/api/auth", authRouter);

app.use("/api/datasets", datasetRoutes);

app.use("/api/anomalies", anomalyRoutes);

app.use("/api/investigations", investigationRoutes);

app.use("/api/reports", reportRoutes);

app.use("/api/validations", validationRoutes);

app.use("/api/dashboard", dashboardRoutes);

app.use((req, res) => {
    return res.status(404).json({
        success: false,
        message: "Route not found",
    });
});


app.listen(PORT,()=>{
    connectDB()
    console.log("server is running..");
})