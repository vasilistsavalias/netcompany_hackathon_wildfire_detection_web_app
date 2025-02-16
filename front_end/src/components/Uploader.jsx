import  { useRef, useState } from "react";
import uploadIcon from "../assets/upload.svg";
import PropTypes from 'prop-types'; // Import PropTypes

function Uploader({ onImageUpload, modelType }) {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!selectedFile) return;

    onImageUpload(selectedFile, modelType); // Pass the file AND modelType
  };

    const getLabel = () => {
        return modelType === "cnn" ? "Fire classification" : "smoke detection";
    }

  return (
    <form className="w-[85%] md:w-[50%] h-[60%]" onSubmit={handleSubmit}>
    <div className="flex flex-col justify-center items-center  w-full container  py-10 px-[10%] space-y-8">
      <h1 className="z-10 font-bold text-xl md:text-3xl text-black text-center">
        {getLabel()}
      </h1>
      <h3 className="text-center">
        If you suspect there might be a fire nearby, please let us determine
        it for you and upload a photo that clearly shows the site!
      </h3>
        <>
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            id={`fileUpload-${modelType}`} // Unique ID
            onChange={handleFileChange}
            accept="image/*"
          />
          <label
            htmlFor={`fileUpload-${modelType}`} // Use unique ID
            className="z-10 flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-800 rounded-lg cursor-pointer hover:bg-gray-100 transition duration-200 ease-in-out"
          >
            <img className="w-10 h-10" src={uploadIcon} alt="Upload Icon" />
            <span className="mt-2 text-sm">
              {selectedFile ? `Selected: ${selectedFile.name}` : "Click to Upload"}
            </span>
          </label>
        </>

      <button
        className="z-10 w-full cursor-pointer bg-black p-3 text-white hover:bg-white hover:text-black rounded-lg transition duration-200 ease-in-out"
        type="submit"
      >
      Examine
      </button>
    </div>
  </form>
  );
}

// Add PropTypes for validation
Uploader.propTypes = {
  onImageUpload: PropTypes.func.isRequired,
  modelType: PropTypes.oneOf(['cnn', 'yolo']).isRequired,
};

export default Uploader;