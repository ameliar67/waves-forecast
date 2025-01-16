// app/not-found.tsx
import React from "react";

// Define the type for the props passed to the 404 page
interface ErrorPageProps {
  errorMessage: string;
  statusCode: number;
  errorDetails?: string;
}

const Custom404Page: React.FC<ErrorPageProps> = ({
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

// Use getServerSideProps to fetch data from Starlette's backend when a 404 error occurs
export async function getServerSideProps() {
  try {
    const res = await fetch("api/404");
    if (!res.ok) {
      throw new Error("Failed to fetch custom 404 data");
    }
    const data = await res.json();
    return {
      props: {
        errorMessage:
          data.detail || "The page you are looking for could not be found.",
        statusCode: data.status_code || 404,
        errorDetails: data.detail || "",
      },
    };
  } catch {
    return {
      props: {
        errorMessage: "The page you are looking for could not be found.",
        statusCode: 404,
        errorDetails: "Could not fetch custom error details from the server.",
      },
    };
  }
}

export default Custom404Page;
