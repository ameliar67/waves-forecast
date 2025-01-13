'use client'
// app/error.tsx
import React from 'react';

// Define the type for the props passed to the 500/error page
interface ErrorPageProps {
  errorMessage: string;
  statusCode: number;
  errorDetails?: string;
}

const Custom500Page: React.FC<ErrorPageProps> = ({ errorMessage, errorDetails, statusCode }) => {
  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <h1>{statusCode} Page Not Found</h1>
      <p>{errorMessage}</p>
      {errorDetails && <pre>{errorDetails}</pre>}
      <p>If you believe this is an error, please contact support.</p>
    </div>
  );
};

// Use getServerSideProps to fetch data from Starlette's backend when a 500 error occurs
export async function getServerSideProps() {
  try {
    const res = await fetch('api/500');
    if (!res.ok) {
      throw new Error('Failed to fetch custom 500 data');
    }
    const data = await res.json();
    return {
      props: {
        errorMessage: data.detail || 'The page you are looking for could not be found.',
        statusCode: data.status_code || 500,
        errorDetails: data.detail || '',
      },
    };
  } catch (error) {
    return {
      props: {
        errorMessage: 'The page you are looking for could not be found.',
        statusCode: 500,
        errorDetails: 'Could not fetch custom error details from the server.',
      },
    };
  }
}

export default Custom500Page;