import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Shield, Sparkles } from 'lucide-react';
import { theme3d } from '../theme3d';

interface GlowingOrbBadgeProps {
  size?: number;
  pulseSpeed?: number;
  icon?: 'shield' | 'sparkles';
  label?: string;
  sublabel?: string;
}

export const GlowingOrbBadge: React.FC<GlowingOrbBadgeProps> = ({
  size = 180,
  icon = 'shield',
  label,
  sublabel,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const scale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 120 },
  });

  // Gentle floating float
  const floatY = Math.sin(frame * 0.06) * 6;
  const pulseScale = 1 + Math.sin(frame * 0.08) * 0.04;
  const ringRotation = frame * 1.2;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        transform: `translateY(${floatY}px) scale(${scale})`,
        transformStyle: 'preserve-3d',
      }}
    >
      {/* Outer Glow Aura */}
      <div
        style={{
          position: 'relative',
          width: size,
          height: size,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Pulsing colored radial halo */}
        <div
          style={{
            position: 'absolute',
            width: size * 1.8,
            height: size * 1.8,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(139, 92, 246, 0.45) 0%, rgba(6, 182, 212, 0.25) 40%, transparent 70%)',
            filter: 'blur(35px)',
            transform: `scale(${pulseScale})`,
            pointerEvents: 'none',
          }}
        />

        {/* Orbiting Neon Ring (matching user Image 1) */}
        <div
          style={{
            position: 'absolute',
            width: size * 1.18,
            height: size * 1.18,
            borderRadius: '50%',
            border: '2px dashed rgba(167, 139, 250, 0.5)',
            transform: `rotate(${ringRotation}deg)`,
            pointerEvents: 'none',
          }}
        />

        {/* Orbiting Neon Accent Particle */}
        <div
          style={{
            position: 'absolute',
            width: size * 1.18,
            height: size * 1.18,
            transform: `rotate(${ringRotation}deg)`,
            pointerEvents: 'none',
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: -4,
              left: '50%',
              width: 10,
              height: 10,
              borderRadius: '50%',
              backgroundColor: theme3d.colors.cyan,
              boxShadow: '0 0 16px #06B6D4, 0 0 30px #06B6D4',
              transform: 'translateX(-50%)',
            }}
          />
        </div>

        {/* Core Glass Sphere with Violet Rim Light */}
        <div
          style={{
            width: size,
            height: size,
            borderRadius: '50%',
            background: 'radial-gradient(130% 130% at 30% 25%, rgba(139, 92, 246, 0.6) 0%, rgba(49, 46, 129, 0.8) 50%, rgba(15, 12, 35, 0.95) 100%)',
            boxShadow: `
              0 20px 50px rgba(0, 0, 0, 0.8),
              inset 0 2px 4px rgba(255, 255, 255, 0.6),
              inset 0 -8px 20px rgba(139, 92, 246, 0.6),
              0 0 35px rgba(139, 92, 246, 0.6)
            `,
            border: '1.5px solid rgba(255, 255, 255, 0.35)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Specular curved reflection on glass orb */}
          <div
            style={{
              position: 'absolute',
              top: '8%',
              left: '18%',
              width: '64%',
              height: '35%',
              borderRadius: '50%',
              background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0) 100%)',
              filter: 'blur(1px)',
              pointerEvents: 'none',
            }}
          />

          {/* Central Emblem Icon */}
          <div
            style={{
              filter: 'drop-shadow(0 4px 12px rgba(255, 255, 255, 0.5)) drop-shadow(0 0 20px rgba(139, 92, 246, 0.8))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon === 'shield' ? (
              <Shield size={size * 0.46} color="#FFFFFF" strokeWidth={2.2} />
            ) : (
              <Sparkles size={size * 0.46} color="#FFFFFF" strokeWidth={2.2} />
            )}
          </div>
        </div>
      </div>

      {/* Label and Sublabel under the orb */}
      {(label || sublabel) && (
        <div
          style={{
            marginTop: 20,
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          {label && (
            <div
              style={{
                fontFamily: theme3d.fonts.sans,
                fontSize: 24,
                fontWeight: 700,
                color: theme3d.colors.textPrimary,
                letterSpacing: '-0.02em',
                textShadow: '0 2px 10px rgba(0, 0, 0, 0.5)',
              }}
            >
              {label}
            </div>
          )}
          {sublabel && (
            <div
              style={{
                fontFamily: theme3d.fonts.sans,
                fontSize: 14,
                fontWeight: 500,
                color: theme3d.colors.textSecondary,
                marginTop: 4,
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
              }}
            >
              {sublabel}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
