import mongoose from "mongoose";

const validationSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
    },

    candidateId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Candidate",
      required: true,
    },

    investigationId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Investigation",
      required: true,
    },

    reportId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Report",
      required: true,
    },

    decision: {
      type: String,
      enum: ["approved", "rejected"],
      required: true,
    },

    notes: {
      type: String,
      default: "",
    },
  },
  {
    timestamps: true,
  }
);

validationSchema.index(
  {
    userId: 1,
    reportId: 1,
  },
  {
    unique: true,
  }
);

const ValidationModel = mongoose.model(
  "Validation",
  validationSchema
);

export default ValidationModel;