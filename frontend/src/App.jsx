import { lazy, Suspense } from "react";
﻿import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import { InvestigationProvider } from "./v5/context/InvestigationContext";
import AppLayout from "./v5/layouts/AppLayout";

const InvestigationPage = lazy(() => import("./v5/pages/InvestigationPage"));
const EvidencePage = lazy(() => import("./v5/pages/EvidencePage"));
const DNSPage = lazy(() => import("./v5/pages/DNSPage"));
const ArchivePage = lazy(() => import("./v5/pages/ArchivePage"));
const AnalyticsPage = lazy(() => import("./v5/pages/AnalyticsPage"));

const UnderworldHome = lazy(() => import("./v5/pages/UnderworldHome"));

import "./v5/styles/platform.css";

export default function App() {
  return (
    <BrowserRouter>
      <InvestigationProvider>
        <Suspense fallback={
          <div role="status" aria-live="polite"
               style={{ padding: "2rem", color: "#b9b9c9" }}>
            Loading PhantomLink...
          </div>
        }>
          <Routes>
            <Route element={<AppLayout />}>
            <Route path="/" element={<UnderworldHome />} />
            <Route path="/investigate" element={<InvestigationPage />} />
            <Route path="/evidence" element={<EvidencePage />} />
            <Route path="/dns" element={<DNSPage />} />
            <Route path="/archive" element={<ArchivePage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Route>
          </Routes>
        </Suspense>
      </InvestigationProvider>
    </BrowserRouter>
  );
}
