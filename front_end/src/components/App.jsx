import { useState } from "react";
import "./App.css";
import background from "../assets/forrest.jpg";
import logo from "../assets/FD-removebg.png";
import Uploader from "./Uploader";

function App() {
  return (
    <>
      <div className="flex justify-center items-center h-screen">
        <img
          src={background}
          alt="background"
          className="w-screen h-screen object-cover"
        />
        <div className="absolute w-full h-full flex flex-col justify-center items-center">
          <img
            className="absolute md:left-5 top-15 md:top-5 z-1 aspect-1 w-28"
            src={logo}
            alt="logo"
          />
          <div className="absolute h-full w-full bg-white opacity-20 p-8 rounded-lg" />
          <Uploader />
        </div>
      </div>
    </>
  );
}

export default App;
