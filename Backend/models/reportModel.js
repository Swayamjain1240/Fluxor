import mongoose from "mongoose";

const hypothesisSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
    },

    confidence: {
      type: Number,
      min: 0,
      max: 1,
    },

    supportingEvidence: [String],

    contradictingEvidence: [String],
  },
  {
    _id: false,
  }
);

const reportSchema = new mongoose.Schema(
  {
    investigationId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Investigation",
      required: true,
      unique: true,
    },

    candidateId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Candidate",
      required: true,
    },

    catalogSummary: {
      type: mongoose.Schema.Types.Mixed,
      default: {},
    },

    hypotheses: {
      type: [hypothesisSchema],
      default: [],
    },

    evidence: {
      type: mongoose.Schema.Types.Mixed,
      default: {},
    },

    confidence: {
      type: Number,
      min: 0,
      max: 1,
      default: 0,
    },

    followupPlan: {
      type: [String],
      default: [],
    },

    reportMarkdown: {
      type: String,
      default: "",
    },
  },
  {
    timestamps: true,
  }
);

const ReportModel = mongoose.model("Report", reportSchema);

export default ReportModel;