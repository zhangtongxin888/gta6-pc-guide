import { Routes, Route } from 'react-router'
import Layout from './components/Layout'
import Home from './pages/Home'
import ReleaseDate from './pages/ReleaseDate'
import PcSpecs from './pages/PcSpecs'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/release-date" element={<ReleaseDate />} />
        <Route path="/pc-specs" element={<PcSpecs />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
