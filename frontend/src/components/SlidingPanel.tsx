import React from "react";
import {motion, AnimatePresence} from "framer-motion";

interface SlidingPanelProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    children?: React.ReactNode;
}

const SlidingPanel: React.FC<SlidingPanelProps> = ({ isOpen, onClose, title = "Panel", children}) => {
    return (
    <AnimatePresence>
      {isOpen && (
        <motion.aside
          initial={{ x: "-100%" }}
          animate={{ x: 0 }}
          exit={{ x: "-100%" }}
          transition={{ type: "tween", duration: 0.3 }}
          className="fixed top-0 left-0 h-full w-64 p-1 bg-white dark:bg-gray-800 shadow-lg border-r border-gray-200 dark:border-gray-700 z-40 flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
            <h2 className="font-semibold text-gray-800 dark:text-gray-100">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto">{children}</div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
};

export default SlidingPanel;
