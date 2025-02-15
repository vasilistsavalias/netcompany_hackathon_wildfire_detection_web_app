import React from "react";
import spinnerIcon from "../assets/spinner.svg";

function Spinner() {
  return (
    <div className="w-full h-full flex justify-center items-center">
      <span className="loader"></span>
    </div>
  );
}

export default Spinner;
