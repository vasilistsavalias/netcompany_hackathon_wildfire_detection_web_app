import PropTypes from "prop-types";

function Results({ results }) {
  if (!results) {
    return <div>No results to display yet.</div>;
  }

  const getClassName = (classId) => {
    if (
      results.class_names &&
      Array.isArray(results.class_names) &&
      results.class_names.length > classId
    ) {
      return results.class_names[classId];
    }
    return `Class ${classId}`;
  };

  return (
    <div className="flex flex-col h-full items-center justify-center space-y-4">
      <h2 className="text-xl font-semibold">Results</h2>
      {results.image_with_boxes && (
        <div className="border-2 border-gray-800 rounded-lg">
          <img
            src={`data:image/jpeg;base64,${results.image_with_boxes}`}
            alt="Processed Image"
            className="h-[35vh] w-full object-cover"
          />
        </div>
      )}
      <p>Processing Time: {results.processing_time.toFixed(2)} seconds</p>

      {results.cnn_probability !== -1.0 && (
        <p style={{ color: results.cnn_probability >= 0.5 ? "red" : "green" }}>
          Fire Classification:{" "}
          {results.cnn_probability >= 0.5 ? "Fire" : "No Fire"} (
          {results.cnn_probability.toFixed(2)})
        </p>
      )}

      {results.yolo_detections && results.yolo_detections.length > 0 ? (
        <div className="w-full my-2 h-full flex flex-col items-center justify-start overflow-y-scroll">
          <h3 className="uppercase text-lg font-semibold">YOLO Detections:</h3>
          <ul>
            {results.yolo_detections.map((detection, index) => (
              <li key={index} className="h-full w-full space-y-2 px-2">
                <p>Confidence: {detection.confidence.toFixed(2)}</p>
                <p>Class: {getClassName(detection.class)}</p>
                <p className="truncate">
                  Bounding Box: {JSON.stringify(detection.bbox)}
                </p>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p>No YOLO detections found.</p>
      )}
    </div>
  );
}

Results.propTypes = {
  results: PropTypes.shape({
    image_with_boxes: PropTypes.string,
    processing_time: PropTypes.number.isRequired,
    cnn_probability: PropTypes.number,
    yolo_detections: PropTypes.arrayOf(
      PropTypes.shape({
        confidence: PropTypes.number.isRequired,
        class: PropTypes.number.isRequired,
        bbox: PropTypes.arrayOf(PropTypes.number).isRequired,
      })
    ),
    id: PropTypes.number,
    timestamp: PropTypes.string,
    class_names: PropTypes.arrayOf(PropTypes.string),
  }),
};

export default Results;
