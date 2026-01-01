import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { ExternalLink } from 'lucide-react'

export default function HelpModal({ isOpen, onClose }) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">¿Qué es LAZOS?</DialogTitle>
        </DialogHeader>

        <div className="space-y-6 text-card-foreground">
          {/* ¿Qué es LAZOS? */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Una red colaborativa</h3>
            <p className="text-muted-foreground">
              Una red colaborativa para reportar mascotas que ves en la calle. Si encontrás un perro o gato perdido,
              subí una foto y ubicación para ayudar a que su dueño lo encuentre.
            </p>
          </section>

          {/* Tu privacidad */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Tu privacidad</h3>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li>No requerimos registro ni cuenta</li>
              <li>No usamos Google Analytics ni trackers</li>
              <li>No vendemos tus datos</li>
            </ul>
          </section>

          {/* Datos abiertos */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Datos abiertos</h3>
            <p className="text-muted-foreground mb-3">
              La información es pública. Podés consumir los avistamientos via API para crear tus propias herramientas.
            </p>
            <div className="bg-muted p-3 rounded-lg">
              <a
                href="https://github.com/nullpointlol01/lazos"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
              >
                Ver en GitHub
                <ExternalLink size={14} />
              </a>
            </div>
          </section>
        </div>
      </DialogContent>
    </Dialog>
  )
}
