import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { HomePage } from './pages/HomePage'
import { StepPage } from './pages/StepPage'
import { LessonPage } from './pages/LessonPage'
import { PracticePage } from './pages/PracticePage'
import { TestPage } from './pages/TestPage'
import { RiskPage } from './pages/RiskPage'
import { ReferencePage } from './pages/ReferencePage'
import { JournalPage } from './pages/JournalPage'
import { SettingsPage } from './pages/SettingsPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="step/:stepId" element={<StepPage />} />
        <Route path="step/:stepId/lesson/:lessonId" element={<LessonPage />} />
        <Route path="step/:stepId/practice" element={<PracticePage />} />
        <Route path="step/:stepId/test" element={<TestPage />} />
        <Route path="journal" element={<JournalPage />} />
        <Route path="risk" element={<RiskPage />} />
        <Route path="reference" element={<ReferencePage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
