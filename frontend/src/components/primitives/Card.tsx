import React from 'react'
import { motion } from 'framer-motion'

export default function Card({children,style}:{children:React.ReactNode,style?:React.CSSProperties}){
  return (
    <motion.div
      className="card"
      style={style}
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      {children}
    </motion.div>
  )
}
