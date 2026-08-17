import cookieParser from "cookie-parser";
import express from "express"
import dotenv from "dotenv";
dotenv.config();
import dns from "dns"
dns.setServers(["1.1.1.1","8.8.8.8"]);
import {errorHandlers} from "./middleware/errorMiddleware.js"
import { connectDB } from "./utils/db.js";

const app = express()

const PORT = process.env.PORT;
app.use(express.json());
app.use(cookieParser());

app.get("/api/health", (req,res)=>{
    res.status(200).json({success: true,message: "Fluxor backend is running",});
});

app.use(errorHandlers);

app.listen(PORT,(req,res)=>{
    connectDB();
    console.log("server is running..");
})