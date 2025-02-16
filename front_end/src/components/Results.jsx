import PropTypes from 'prop-types';

function Results({ results }) {
    if (!results) {
        return <div>No results to display yet.</div>;
    }

    // Helper function to get class name, handling potential errors
    const getClassName = (classId) => {
        if (results.class_names && Array.isArray(results.class_names) && results.class_names.length > classId) {
            return results.class_names[classId];
        }
        return `Class ${classId}`; // Default if class name is not found
    };

    return (
        <div>
            <h2>Results</h2>
            {results.image_with_boxes && (
                <img src={`data:image/jpeg;base64,${results.image_with_boxes}`} alt="Processed Image" />
            )}
            <p>Processing Time: {results.processing_time.toFixed(2)} seconds</p>

            {/* Display CNN results conditionally */}
            {results.cnn_probability !== -1.0 && (
                <p style={{ color: results.cnn_probability >= 0.5 ? 'red' : 'green' }}>
                    Fire Classification: {results.cnn_probability >= 0.5 ? 'Fire' : 'No Fire'} ({results.cnn_probability.toFixed(2)})
                </p>
            )}

            {/* Display YOLO results conditionally */}
            {results.yolo_detections && results.yolo_detections.length > 0 ? (
                <>
                    <h3>YOLO Detections:</h3>
                    <ul>
                        {results.yolo_detections.map((detection, index) => (
                            <li key={index}>
                                <p>Confidence: {detection.confidence.toFixed(2)}</p>
                                <p>Class: {getClassName(detection.class)}</p> {/* Use helper function */}
                                <p>Bounding Box: {JSON.stringify(detection.bbox)}</p>
                            </li>
                        ))}
                    </ul>
                </>
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
        class_names: PropTypes.arrayOf(PropTypes.string), // Add class_names to propTypes
    }),
};

export default Results;