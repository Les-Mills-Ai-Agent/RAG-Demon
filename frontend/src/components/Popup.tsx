interface PopupProps {
    title: string,
    description: string,
    action: string,
    onSuccess: () => void,
    onClose: () => void
}

const Popup: React.FC<PopupProps> = ({title, description, action, onSuccess, onClose}) => {
    return (
        <div className="fixed inset-0 z-50">
            {/* Backdrop with blur */}
            <div
                className="absolute inset-0 bg-black/30 backdrop-blur-[2px]"
                aria-hidden="true"
            />
            <div className="absolute inset-0 flex items-end sm:items-center justify-center p-4">
                <div
                    className="w-full max-w-sm rounded-2xl bg-white/95 dark:bg-gray-800/95 shadow-xl border border-gray-200/70 dark:border-gray-700/60
                               transition-all duration-150 ease-out
                               animate-[fadeIn_120ms_ease-out] sm:animate-[pop_140ms_ease-out]"
                    style={{
                        // keyframes in inline style fallback
                        // fadeIn: opacity in; pop: scale + opacity in
                        animationName: undefined,
                    }}
                >
                    {/* Header */}
                    <div className="px-5 py-3 border-b border-gray-200/70 dark:border-gray-700/60">
                        <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                            {title}
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="p-5">
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                            {description}
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="px-5 py-3 gap-2 border-t border-gray-200/70 dark:border-gray-700/60 flex justify-end">
                        <button
                            onClick={onClose}
                            className="px-3 py-1.5 rounded-xl border border-gray-300 dark:border-gray-600
                                   text-sm hover:bg-gray-50 dark:hover:bg-gray-700"
                        >
                            Close
                        </button>
                        <button
                            onClick={onSuccess}
                            className="px-3 py-1.5 rounded-xl border border-red-300 dark:border-red-600
                                   text-sm text-white bg-red-500 hover:bg-red-600 dark:hover:bg-red-700"
                        >
                            {action}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Popup;
