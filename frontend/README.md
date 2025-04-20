# PaperShelf Frontend

This is the React frontend for the PaperShelf application, an intelligent academic paper management and query system powered by RAG (Retrieval-Augmented Generation).

## Features

- **Home Page**: View a list of chat sessions and access the main features
- **Upload Papers**: Upload PDF papers to the system for processing and querying
- **Query Papers**: Ask questions about your uploaded papers and get AI-generated answers

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- npm or yarn
- PaperShelf backend running (default: http://localhost:8000)

### Installation

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

3. Start the development server:
   ```
   npm start
   ```
   or
   ```
   yarn start
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Building for Production

To build the app for production:

```
npm run build
```
or
```
yarn build
```

This creates a `build` directory with optimized production files.

## Docker

A Dockerfile is provided to containerize the frontend. To build and run:

```
docker build -t papershelf-frontend .
docker run -p 3000:80 papershelf-frontend
```

## Project Structure

- `public/`: Static files
- `src/`: Source code
  - `components/`: React components
    - `Home.js`: Home page component
    - `Upload.js`: Upload papers component
    - `Query.js`: Query papers component
    - `Navbar.js`: Navigation component
  - `App.js`: Main application component
  - `index.js`: Application entry point

## API Communication

The frontend communicates with the backend API using axios. The main endpoints used are:

- `GET /sessions`: Fetch chat sessions
- `POST /upload`: Upload PDF files
- `POST /query`: Submit queries about papers

## Development Notes

- The application uses React Router for navigation
- Local storage is used to persist query history between sessions
- The proxy setting in package.json redirects API requests to the backend server