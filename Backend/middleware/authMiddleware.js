import jwt from "jsonwebtoken"

export const authMiddleware =  (req,res, next) => {
    try {
        const authHeader = req.headers.authorization;
        if(!authHeader){
            return res.status(401).json({message:"your authorization header missing"});
        };

        const auth = authHeader.startsWith("Bearer ")
        if(!auth){
            return res.status(401).json({message:"you access token missing"});
        };

        const token = authHeader.split(" ")[1];

        const decode = jwt.verify(token, process.env.ACCESS_TOKEN_SECRET);
        if(!decode){
            return res.status(401).json({message:"your token cant verify"});
        };

        req.user=decode;
        next();

    } catch (error) {
         return res.status(500).json({success: false,message: "internal server error",});
    }   
}