import mongoose from "mongoose";

const datasetSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true,
    },

    name: {
      type: String,
      required: true,
      trim: true,
    },

    description: {
      type: String,
      default: "",
    },

    source: {
      type: String,
      enum: ["TESS", "KEPLER", "ZTF", "GCN", "OTHER"],
      required: true,
    },

    dataPath: {
      type: String,
      required: true,
    },

    status: {
      type: String,
      enum: ["uploaded", "processing", "completed", "failed"],
      default: "uploaded",
    },
  },
  {
    timestamps: true,
  }
);

const DatasetModel = mongoose.model("Dataset", datasetSchema);

export default DatasetModel;