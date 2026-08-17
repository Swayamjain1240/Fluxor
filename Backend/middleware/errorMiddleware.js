import express from "express"

export const errorHandlers = (err,req,res,next) =>{
   console.error(err);

    res.status(err.statusCode|| 500).json({message: err.message || " internal server error "});
};