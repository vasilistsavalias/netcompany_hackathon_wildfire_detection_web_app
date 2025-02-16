import React, { useRef, useState } from "react";
import uploadIcon from "../assets/upload.svg";
import Spinner from "./Spinner";

function Uploader() {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) return;

    setLoading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();

        let errorMessage = `HTTP error! Status: ${response.status}, Message: ${
          errorData.error || "Unknown error"
        }`;

        if (
          (response.status === 500 &&
            errorData.error.includes("Error communicating with AI model")) ||
          errorData.error.includes("Error processing AI model response")
        ) {
          errorMessage =
            "Failed to communicate with the AI model. Please ensure the AI model API is running correctly.";
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log("Upload successful:", data);
      alert("File uploaded successfully!");

      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = null;
      }
    } catch (error) {
      console.error("Upload error:", error);

      if (error.message.includes("Failed to fetch")) {
        setUploadError(
          "Failed to connect to the server.  Please ensure the backend and AI model API are running."
        );
      } else if (error.message.includes("AI Model failed")) {
        setUploadError(
          "Failed to communicate with the AI model. Please ensure the AI model API is running correctly."
        );
      } else {
        setUploadError(error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="w-[85%] md:w-[50%] h-[60%]" onSubmit={handleSubmit}>
      <div className="flex flex-col justify-center items-center h-full w-full container mx-auto py-10 px-[10%] space-y-8">
        <h1 className="z-10 font-bold text-xl md:text-3xl text-black text-center">
          Upload a photo
        </h1>
        <h3 className="text-center">
          If you suspect there might be a fire nearby, please let us determine
          it for you and upload a photo that clearly shows the site!
        </h3>

        {loading ? (
          <div className="h-32">
            <Spinner />
          </div>
        ) : (
          <>
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              id="fileUpload"
              onChange={handleFileChange}
            />

            <label
              htmlFor="fileUpload"
              className="z-10 flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-800 rounded-lg cursor-pointer hover:bg-gray-100 transition duration-200 ease-in-out"
            >
              <img className="w-10 h-10" src={uploadIcon} alt="Upload Icon" />
              <span className="mt-2 text-sm">
                {selectedFile
                  ? `Uploaded: ${selectedFile.name}`
                  : "Click to Upload"}
              </span>
            </label>
          </>
        )}

        {uploadError && <div className="text-red-500">{uploadError}</div>}

        <button
          className="z-10 w-full cursor-pointer bg-black p-3 text-white hover:bg-white hover:text-black rounded-lg transition duration-200 ease-in-out"
          type="submit"
          disabled={loading || !selectedFile} // Disable if loading or no file selected
        >
          {loading ? "Searching for possible fire..." : "Examine"}
        </button>
      </div>
    </form>
  );
}

export default Uploader;
