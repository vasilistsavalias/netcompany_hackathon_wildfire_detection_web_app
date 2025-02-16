import { useState } from 'react'; // Only import useState
import './App.css';
import background from '../assets/forrest.jpg';
import logo from '../assets/FD-removebg.png';
import Uploader from './Uploader';
import Results from './Results';
import axios from 'axios';

function App() {
  const [cnnResults, setCnnResults] = useState(null);
  const [yoloResults, setYoloResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResults, setShowResults] = useState(false); // Control when to show results

  const handleImageUpload = async (imageFile, modelType) => {
    setLoading(true);
    setError(null);
    // Clear previous results of the *opposite* type:
    if (modelType === 'cnn') {
        setYoloResults(null);
    } else {
        setCnnResults(null);
    }

    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('model_type', modelType);

    try {
      const response = await axios.post('http://127.0.0.1:8080/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (modelType === 'cnn') {
        setCnnResults(response.data);
      } else {
        setYoloResults(response.data);
      }
      setShowResults(true); // Show results after successful upload

    } catch (error) {
      if (error.response) {
        setError(error.response.data.error || 'An error occurred.');
      } else {
        setError('An error occurred.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoBack = () => {
    setShowResults(false);
    setCnnResults(null);   // Clear results
    setYoloResults(null);
  };

  return (
    <>
      <div className="flex justify-center items-center h-screen">
        <img src={background} alt="background" className="w-screen h-screen object-cover" />
        <div className="absolute w-full h-full flex flex-col justify-center items-center">
          <img className="absolute md:left-5 top-15 md:top-5 z-1 aspect-1 w-28" src={logo} alt="logo" />
          <div className="absolute h-full w-full bg-white opacity-20 p-8 rounded-lg" />

          {!showResults ? (
            // Show uploaders when showResults is false
            <div className="flex flex-row space-x-4 w-full justify-center">
              <div className="flex flex-col items-center">
                <Uploader onImageUpload={(file) => handleImageUpload(file, 'cnn')} modelType="cnn" />
                {/* {cnnLoading && <p>Processing CNN Image...</p>}  Unified loading message */}
              </div>
              <div className="flex flex-col items-center">
                <Uploader onImageUpload={(file) => handleImageUpload(file, 'yolo')} modelType="yolo" />
                {/* {yoloLoading && <p>Processing YOLO Image...</p>}  Unified loading message */}
              </div>
            </div>
          ) : (
            // Show results and back button when showResults is true
            <>
              <button onClick={handleGoBack} className="absolute top-4 left-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                Back
              </button>
              {/* Display Results based on which model was used */}
              {cnnResults && <Results results={cnnResults} />}
              {yoloResults && <Results results={yoloResults} />}
            </>
          )}
            {loading && <p>Processing...</p>} {/* Unified loading message */}
          {error && <p className="error">{error}</p>}
        </div>
      </div>
    </>
  );
}

export default App;