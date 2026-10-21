import { Outlet } from "react-router-dom";
import Sidebar from "./components/Layout/Sidebar";
import TopBar from "./components/Layout/TopBar";

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar title="NetSentinel" />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
