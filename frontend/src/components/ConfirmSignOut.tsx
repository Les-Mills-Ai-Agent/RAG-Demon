import { useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";

type Props = {
  open: boolean;
  onCancel: () => void;
  onConfirm: () => void;
};

export default function ConfirmSignOut({ open, onCancel, onConfirm }: Props) {
  // Close on ESC
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onCancel();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onCancel]);

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 z-[9998] bg-black/50 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
          {/* Modal */}
          <motion.div
            className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            aria-modal="true"
            role="dialog"
          >
            <motion.div
              className="w-full max-w-md rounded-2xl bg-white dark:bg-gray-900 shadow-2xl p-6"
              initial={{ scale: 0.9, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.95, y: 10, opacity: 0 }}
              transition={{ type: "spring", stiffness: 220, damping: 18 }}
            >
              <div className="flex items-center gap-3 mb-4">
                <motion.div
                  className="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center"
                  initial={{ rotate: -10 }}
                  animate={{ rotate: 0 }}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" className="text-red-600 dark:text-red-400">
                    <path fill="currentColor" d="M16 13v-2H7V8l-5 4l5 4v-3h9zM20 3h-8v2h8v14h-8v2h8q.825 0 1.413-.588T22 19V5q0-.825-.588-1.413T20 3Z"/>
                  </svg>
                </motion.div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Sign out?
                </h2>
              </div>

              <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                You’re about to sign out of your session. You can sign back in anytime.
              </p>

              <div className="flex items-center justify-end gap-3">
                <motion.button
                  whileTap={{ scale: 0.98 }}
                  onClick={onCancel}
                  className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800"
                >
                  Cancel
                </motion.button>
                <motion.button
                  whileTap={{ scale: 0.98 }}
                  onClick={onConfirm}
                  className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700"
                >
                  Yes, sign me out
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
