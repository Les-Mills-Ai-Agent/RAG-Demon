import { motion, AnimatePresence } from "framer-motion";

export default function LoginCelebration({
  visible,
  userEmail,
}: {
  visible: boolean;
  userEmail: string;
}) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {/* card */}
          <motion.div
            className="relative w-72 h-72 rounded-3xl bg-white dark:bg-gray-900 shadow-2xl flex items-center justify-center"
            initial={{ scale: 0.8, rotate: -6 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 220, damping: 18 }}
          >
            {/* animated ring */}
            <motion.div
              className="absolute inset-0 rounded-3xl"
              style={{
                background:
                  "conic-gradient(from 90deg at 50% 50%, #60a5fa, #34d399, #f59e0b, #a78bfa, #60a5fa)",
                WebkitMask:
                  "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                WebkitMaskComposite: "xor",
                padding: 3,
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            />

            {/* checkmark */}
            <motion.svg
              width="110"
              height="110"
              viewBox="0 0 110 110"
              className="relative z-10"
            >
              <motion.circle
                cx="55"
                cy="55"
                r="48"
                fill="none"
                strokeWidth="8"
                stroke="rgba(16,185,129,0.25)"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
              <motion.path
                d="M32 58 L50 74 L78 40"
                fill="none"
                stroke="#10b981"
                strokeWidth="8"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 0.25, duration: 0.6, ease: "easeOut" }}
              />
            </motion.svg>

            {/* label */}
            <div className="absolute bottom-4 left-0 right-0 text-center px-4">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Logged in as
              </div>
              <div className="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">
                {userEmail}
              </div>
            </div>

            {/* tiny confetti dots */}
            {[...Array(18)].map((_, i) => (
              <motion.span
                key={i}
                className="absolute w-2 h-2 rounded-full"
                style={{
                  backgroundColor: ["#60a5fa", "#34d399", "#f59e0b", "#a78bfa"][
                    i % 4
                  ],
                }}
                initial={{ x: 0, y: 0, opacity: 0 }}
                animate={{
                  x: (Math.random() - 0.5) * 260,
                  y: (Math.random() - 0.5) * 260,
                  opacity: [0, 1, 0],
                }}
                transition={{ delay: 0.2 + i * 0.02, duration: 1.1 }}
              />
            ))}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
