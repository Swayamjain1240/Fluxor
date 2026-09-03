import mongoose from "mongoose";

const investigationSchema = new mongoose.Schema(
  {
    candidateId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Candidate",
      required: true,
      index: true,
    },

    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
    },

    status: {
      type: String,
      enum: [
        "queued",
        "running",
        "completed",
        "failed",
        "needs_review",
      ],
      default: "queued",
      index: true,
    },

    triagePriority: {
      type: String,
      enum: ["LOW", "MEDIUM", "HIGH"],
    },

    currentStep: {
      type: String,
      default: "queued",
    },

    iterationCount: {
      type: Number,
      default: 0,
    },

    confidence: {
      type: Number,
      default: 0,
    },

    startedAt: {
      type: Date,
      default: null,
    },

    completedAt: {
      type: Date,
      default: null,
    },

    errorMessage: {
      type: String,
      default: null,
    },
  },
  {
    timestamps: true,
  }
);

const InvestigationModel = mongoose.model(
  "Investigation",
  investigationSchema
);

export default InvestigationModel;