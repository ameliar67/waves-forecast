import React from "react";

// Define the type for the props passed to the 404 page
interface ErrorPageProps {
  errorMessage: string;
  statusCode: number;
  errorDetails?: string;
}

export const Custom404Page: React.FC<ErrorPageProps> = ({
  errorMessage,
  errorDetails,
  statusCode,
}) => {
  return (
    <div style={{ textAlign: "center", padding: "50px" }}>
      <h1>{statusCode} Page Not Found</h1>
      <p>{errorMessage}</p>
      {errorDetails && <pre>{errorDetails}</pre>}
      <p>If you believe this is an error, please contact support.</p>
    </div>
  );
};
