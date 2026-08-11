import React from 'react'
import Topbar from './Topbar'
import Sidebar from './Sidebar'
import { Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

export default function Shell() {
  const location = useLocation()
  return (
    <div className="app-shell">
      <Topbar />
      <div className="shell-body">
        <Sidebar />
        <main className="shell-content">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.26, ease: 'easeOut' }}
            >
              <div className="container">
                <Outlet />
              </div>
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}