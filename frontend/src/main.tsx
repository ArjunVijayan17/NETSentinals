import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App";
import Overview from "./pages/Overview";
import Analyze from "./pages/Analyze";
import Results from "./pages/Results";
import ModelEval from "./pages/ModelEval";
import History from "./pages/History";
import "./index.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Overview /> },
      { path: "analyze", element: <Analyze /> },
      { path: "analyses/:id", element: <Results /> },
      { path: "models", element: <ModelEval /> },
      { path: "history", element: <History /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
