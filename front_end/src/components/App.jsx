import { useState } from "react"; // Only import useState
import "./App.css";
import background from "../assets/forrest.jpg";
import logo from "../assets/FD-removebg.png";
import Uploader from "./Uploader";
import Results from "./Results";
import axios from "axios";
import Spinner from "./Spinner";

function ContentPlaceholder({ children }) {
  return (
    <div className="flex flex-col space-x-4 py-4 justify-center bg-white w-full md:w-[70%] h-full md:h-[65%] container drop-shadow-xl">
      {children}
    </div>
  );
}

function App() {
  const [cnnResults, setCnnResults] = useState(null);
  const [yoloResults, setYoloResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const handleImageUpload = async (imageFile, modelType) => {
    setLoading(true);
    setError(null);

    if (modelType === "cnn") {
      setYoloResults(null);
    } else {
      setCnnResults(null);
    }

    const formData = new FormData();
    formData.append("image", imageFile);
    formData.append("model_type", modelType);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8080/predict",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      if (modelType === "cnn") {
        setCnnResults(response.data);
      } else {
        setYoloResults(response.data);
      }
      setShowResults(true);
    } catch (error) {
      if (error.response) {
        setError(error.response.data.error || "An error occurred.");
      } else {
        setError("An error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoBack = () => {
    setShowResults(false);
    setCnnResults(null);
    setYoloResults(null);
  };

  return (
    <>
      <div className="flex justify-center items-center h-screen">
        <img
          src={background}
          alt="background"
          className="w-screen h-screen object-cover"
        />
        <div className="absolute w-full h-full flex flex-col justify-center items-center">
          <div className="absolute h-full w-full bg-white opacity-20 p-8 rounded-lg" />
          {showResults ? (
            <ContentPlaceholder>
              <button
                onClick={handleGoBack}
                className="absolute top-4 left-4 bg-black text-white transition-colors py-2 px-4 rounded"
              >
                Back
              </button>
              {cnnResults && <Results results={cnnResults} />}
              {yoloResults && <Results results={yoloResults} />}
            </ContentPlaceholder>
          ) : loading ? (
            <ContentPlaceholder>
              <Spinner />
            </ContentPlaceholder>
          ) : error ? (
            <ContentPlaceholder>
              <p className="error">{error}</p>
            </ContentPlaceholder>
          ) : (
            <ContentPlaceholder>
              <div className="flex justify-center items-center space-x-2">
                <img className="w-20" src={logo} alt="logo" />
                <h1 className="text-center text-xl font-bold">
                  Fire Detection
                </h1>
              </div>

              <h3 className="text-center text-lg mx-auto w-[60%] py-2">
                If you suspect there might be a fire nearby, please let us
                determine it for you and upload a photo that clearly shows the
                site!
              </h3>
              <div className="flex flex-col justify-center items-center">
                <Uploader
                  onImageUpload={(file) => handleImageUpload(file, "cnn")}
                  modelType="cnn"
                />
              </div>
              <div className="flex flex-col items-center">
                <Uploader
                  onImageUpload={(file) => handleImageUpload(file, "yolo")}
                  modelType="yolo"
                />
              </div>
            </ContentPlaceholder>
          )}
        </div>
      </div>
    </>
  );
}

export default App;
