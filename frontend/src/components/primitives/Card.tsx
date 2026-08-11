import { motion } from 'framer-motion'
import React from 'react'

export default function Card({
  children,
  style,
  hover = false,
}: {
  children: React.ReactNode
  style?: React.CSSProperties
  hover?: boolean
}) {
  return (
    <motion.div
      className="card"
      style={style}
      whileHover={hover ? { y: -4 } : undefined}
      transition={{ type: 'spring', stiffness: 320, damping: 26 }}
    >
      {children}
    </motion.div>
  )
}