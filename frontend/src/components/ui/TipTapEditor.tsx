"use client";

import HorizontalRule from "@tiptap/extension-horizontal-rule";
import { Image as TipTapImage } from "@tiptap/extension-image";
import { Link } from "@tiptap/extension-link";
import Typography from "@tiptap/extension-typography";
import { Placeholder } from "@tiptap/extension-placeholder";
import TextAlign from "@tiptap/extension-text-align";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import type { VariantProps } from "class-variance-authority";
import { cva } from "class-variance-authority";
import clsx from "clsx";
import { useEffect, useState } from "react";
import CodeBlock from "@tiptap/extension-code-block";

export const tipTapEditorDivStyle = "whitespace-normal break-words text-body";

const tipTapEditorStyles = cva(
  [
    "cursor-text border-transparent before:text-placeholder empty:before:content-[attr(placeholder)] focus:border-transparent focus:outline-none focus:ring-0 max-w-3xl mx-auto space-y-3",
    tipTapEditorDivStyle,
  ],
  {
    variants: {
      variant: {
        heading1: "text-heading2 font-bold md:text-heading1",
        heading2: "text-heading2 font-bold",
        heading3: "text-heading3 font-bold",
        button1: "text-body font-bold",
        button2: "text-body font-medium",
        button3: "text-body font-normal",
        body: "text-body font-normal",
        caption1: "text-caption font-bold",
        caption2: "text-caption font-normal",
        description: "text-description font-normal",
        label: "text-label font-semibold",
        smallLabel: "text-smallLabel font-semibold",
      },
      fixed: { true: "", false: "" },
      color: {
        primary: "!text-primary",
        secondary: "!text-secondary",
        success: "!text-success",
        error: "!text-error",
        inherit: "!text-inherit",
      },
      cursor: {
        text: "!cursor-text",
        pointer: "!cursor-pointer",
      },
    },
    compoundVariants: [
      { fixed: true, variant: "heading1", class: "!text-heading1" },
      { fixed: true, variant: "heading2", class: "!text-heading2" },
      { fixed: true, variant: "heading3", class: "!text-heading3" },
    ],
    defaultVariants: {
      variant: "body",
      fixed: false,
    },
  },
);

type Without<T, K> = Pick<T, Exclude<keyof T, K>>;

export interface TipTapEditorProps
  extends VariantProps<typeof tipTapEditorStyles>,
    Without<React.ComponentProps<"div">, "color"> {
  defaultAlign: "left" | "center" | "right";
  content: string;
  editable: boolean;
  placeholder?: string;
  isMenuHidden?: boolean;
  outputFormat?: 'html' | 'markdown';
  onUpdate?: (content: string) => void;
}

export const TipTapEditor = ({
  variant,
  fixed,
  color,
  cursor,
  defaultAlign,
  content,
  editable,
  placeholder,
  isMenuHidden,
  outputFormat = 'html',
  onUpdate,
  ...divComponentProps
}: TipTapEditorProps) => {
  const [isEditorFocused, setIsEditorFocused] = useState(false);

  const editor = useEditor({
    editorProps: {
      attributes: {
        class: clsx(
          tipTapEditorStyles({ variant, fixed, color, cursor }),
          divComponentProps.className,
        ),
      },
    },
    onUpdate: (props) => {
      let outputContent: string;
      
      if (props.editor.isEmpty) {
        outputContent = "";
      } else {
        outputContent = outputFormat === 'markdown' 
          ? props.editor.storage.markdown.getMarkdown()
          : props.editor.getHTML();
      }
      
      if (onUpdate) onUpdate(outputContent);
    },
    extensions: [
      Typography,
      StarterKit.configure({
        bulletList: {
          HTMLAttributes: {
            // center a list: https://www.w3schools.com/howto/howto_css_center-list.asp
            // bullet inside div: https://stackoverflow.com/questions/1461015/why-dont-ul-bullets-stay-within-their-containing-div
            class: "inline-flex flex-col list-disc text-left ml-[1.25em]",
          },
        },
        orderedList: {
          HTMLAttributes: {
            // center a list: https://www.w3schools.com/howto/howto_css_center-list.asp
            // bullet inside div: https://stackoverflow.com/questions/1461015/why-dont-ul-bullets-stay-within-their-containing-div
            class: "inline-flex flex-col list-decimal text-left ml-[1.25em]",
          },
        },
        heading: {
          HTMLAttributes: {
            class: "text-xl font-bold",
          },
        },
        paragraph: {
          HTMLAttributes: {
            class: "m-0",
          },
        },
      }),
      Placeholder.configure({
        includeChildren: true,
        showOnlyCurrent: false,
        placeholder: ({ node }) => {
          if (node.type.name === "detailsSummary") {
            return "Toggle";
          }
          return placeholder || "";
        },
        emptyEditorClass:
          "first:before:text-secondary first:before:float-left first:before:content-[attr(data-placeholder)] first:before:pointer-events-none first:before:h-0",
      }),
      Link.configure({
        HTMLAttributes: {
          class: "underline font-medium cursor-pointer",
        },
      }),
      TipTapImage.configure({
        // We need this to be inline so we can use TextAlign on the element
        // Ref: https://github.com/ueberdosis/tiptap/issues/1481#issuecomment-867849915
        inline: true,
        HTMLAttributes: {
          // https://stackoverflow.com/a/73667926
          class: "m-auto",
        },
      }),
      HorizontalRule,
      TextAlign.configure({
        types: ["paragraph"],
        defaultAlignment: defaultAlign,
      }),
      CodeBlock.configure({
        HTMLAttributes: {
          class: "bg-gray-100 p-4 rounded-lg my-2 font-mono text-sm",
        },
      }),
    ],
    content,
    editable,
  });

  useEffect(() => {
    if (!editor || content == null) return;

    // we need to remember the cursor position and then restore it
    const { from, to } = editor.state.selection;

    // must preserve whitespace b/c whitespace is by default collapsed as per HTML's rules.
    // however, we want to just preserve the whitespaces as it is.
    editor.commands.setContent(content, false, { preserveWhitespace: true });

    // restore cursor position
    editor.commands.setTextSelection({ from, to });
  }, [content, editor]);

  // Tailwind's break-words is not effective so we manually style here
  return (
    <div
      className="flex flex-col gap-y-2"
      onFocus={() => setIsEditorFocused(true)}
    >
      <EditorContent style={{ wordBreak: "break-word" }} editor={editor} />
    </div>
  );
};