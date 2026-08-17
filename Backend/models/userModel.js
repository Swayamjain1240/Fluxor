import mongoose from "mongoose";
import bcrypt from "bcrypt"

const userSchema = new mongoose.Schema({
    name:{
        type:String,
        required:true,
        trin:true
    },
    email:{
        type:String,
        required:true,
        unique:true,
        lowercase:true,
        trim:true,
    },
    password:{
        type:String,
        required:true,
        minlength: 6,
    },
    refreshToken: {
      type: String,
      default: null,
    },
},{timestamps: true});

const UserModel = mongoose.model("User", userSchema);
export default UserModel;