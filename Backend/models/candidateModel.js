import mongoose from "mongoose";

const candidateSchema = new mongoose.Schema(
  {
    datasetId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Dataset",
      required: true,
      index: true,
    },

    objectId: {
      type: String,
      required: true,
      index: true,
    },

    anomalyScore: {
      type: Number,
      required: true,
      min: 0,
      max: 1,
    },

    priority: {
      type: String,
      enum: ["LOW", "MEDIUM", "HIGH"],
      default: "LOW",
      index: true,
    },

    metadata: {
      ra: Number,
      dec: Number,
      survey: String,
      magnitude: Number,
    },

    lightCurve: [
      {
        time: Number,
        flux: Number,
      },
    ],

    status: {
      type: String,
      enum: [
        "detected",
        "queued",
        "running",
        "completed",
        "failed",
        "needs_review",
      ],
      default: "detected",
    },
  },
  {
    timestamps: true,
  }
);

candidateSchema.index({
  datasetId: 1,
  anomalyScore: -1,
});

const CandidateModel = mongoose.model("Candidate", candidateSchema);

export default CandidateModel;