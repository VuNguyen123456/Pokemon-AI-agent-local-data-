/**
 * Pokemon Stats Modal JavaScript
 * 
 * Handles displaying Pokemon stats from PokeAPI when clicking on Pokemon sprites.
 * This file is separated from app.py for better organization and maintainability.
 */

console.log('[Pokemon Stats] ====== SCRIPT STARTING ======');
(function() {
    'use strict';
    console.log('[Pokemon Stats] Script loaded and executing');
    console.log('[Pokemon Stats] window object:', typeof window);
    console.log('[Pokemon Stats] document object:', typeof document);
    
    // PokeAPI base URL - centralized here for easy updates
    const POKEAPI_BASE_URL = 'https://pokeapi.co/api/v2';
    
    // Stat name mappings for display
    const STAT_NAMES = {
        'hp': 'HP',
        'attack': 'Attack',
        'defense': 'Defense',
        'special-attack': 'Sp. Atk',
        'special-defense': 'Sp. Def',
        'speed': 'Speed'
    };
    
    /**
     * Fetch Pokemon data from PokeAPI
     * @param {string} nameToTry - Pokemon name to fetch
     * @returns {Promise<Object>} Pokemon data from API
     */
    function fetchPokemon(nameToTry) {
        console.log('[Pokemon Stats] Fetching Pokemon:', nameToTry);
        const url = `${POKEAPI_BASE_URL}/pokemon/${nameToTry}`;
        console.log('[Pokemon Stats] API URL:', url);
        
        return fetch(url)
            .then(response => {
                console.log('[Pokemon Stats] API Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`Pokemon not found: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('[Pokemon Stats] API Data received:', data);
                const name = data.species.name;
                const art = data.sprites.other['official-artwork']?.front_default || 
                          data.sprites.front_default || 
                          data.sprites.other?.dream_world?.front_default || '';
                const stats = data.stats;
                
                console.log('[Pokemon Stats] Parsed data:', {name, art: !!art, statsCount: stats.length});
                
                let statsHTML = '';
                if (art) {
                    statsHTML += `<div class="pokemon-stats-art"><img src="${art}" alt="${name}" /></div>`;
                }
                statsHTML += '<ul class="pokemon-stats-list">';
                
                stats.forEach(stat => {
                    const statName = stat.stat.name;
                    const statValue = stat.base_stat;
                    const displayName = STAT_NAMES[statName] || statName;
                    statsHTML += `
                        <li class="pokemon-stat-item">
                            <span class="pokemon-stat-name">${displayName}</span>
                            <span class="pokemon-stat-value">${statValue}</span>
                        </li>
                    `;
                });
                
                statsHTML += '</ul>';
                
                const bodyEl = document.getElementById('pokemon-stats-body');
                const titleEl = document.getElementById('pokemon-stats-title');
                
                if (bodyEl && titleEl) {
                    bodyEl.innerHTML = statsHTML;
                    titleEl.textContent = name.charAt(0).toUpperCase() + name.slice(1).replace(/-/g, ' ');
                    console.log('[Pokemon Stats] Stats displayed successfully');
                } else {
                    console.error('[Pokemon Stats] ERROR: Modal elements missing when updating!');
                }
            })
            .catch(error => {
                console.error('[Pokemon Stats] Error in fetchPokemon:', error);
                throw error;
            });
    }
    
    /**
     * Show Pokemon stats modal with data from PokeAPI
     * @param {string} pokemonName - Pokemon name in PokeAPI format
     * @param {string} baseName - Base Pokemon name for fallback
     */
    window.showPokemonStats = function(pokemonName, baseName) {
        try {
            console.log('[Pokemon Stats] showPokemonStats called with:', {pokemonName, baseName});
            
            if (!pokemonName) {
                console.error('[Pokemon Stats] ERROR: pokemonName is missing!');
                return;
            }
            
            // Create or get modal
            let modal = document.getElementById('pokemon-stats-modal');
            console.log('[Pokemon Stats] Modal found:', !!modal);
            
            if (!modal) {
                console.log('[Pokemon Stats] Creating new modal');
                modal = document.createElement('div');
                modal.id = 'pokemon-stats-modal';
                modal.className = 'pokemon-stats-modal';
                modal.innerHTML = `
                    <div class="pokemon-stats-content">
                        <div class="pokemon-stats-header">
                            <h2 class="pokemon-stats-title" id="pokemon-stats-title">Loading...</h2>
                            <button class="pokemon-stats-close" id="pokemon-stats-close-btn">&times;</button>
                        </div>
                        <div id="pokemon-stats-body">
                            <div class="pokemon-stats-loading">Loading stats...</div>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                console.log('[Pokemon Stats] Modal appended to body');
                
                // Close on background click
                modal.addEventListener('click', function(e) {
                    if (e.target === modal) {
                        console.log('[Pokemon Stats] Background clicked, closing modal');
                        window.closePokemonStats();
                    }
                });
                
                // Close button handler
                const closeBtn = document.getElementById('pokemon-stats-close-btn');
                if (closeBtn) {
                    closeBtn.addEventListener('click', function(e) {
                        console.log('[Pokemon Stats] Close button clicked');
                        e.stopPropagation();
                        window.closePokemonStats();
                    });
                }
            }
            
            modal.style.display = 'block';
            console.log('[Pokemon Stats] Modal displayed');
            
            const bodyEl = document.getElementById('pokemon-stats-body');
            const titleEl = document.getElementById('pokemon-stats-title');
            
            if (!bodyEl || !titleEl) {
                console.error('[Pokemon Stats] ERROR: Modal elements not found!', {bodyEl: !!bodyEl, titleEl: !!titleEl});
                return;
            }
            
            bodyEl.innerHTML = '<div class="pokemon-stats-loading">Loading stats...</div>';
            titleEl.textContent = pokemonName.charAt(0).toUpperCase() + pokemonName.slice(1).replace(/-/g, ' ');
            
            // Try the full name first, then fallback to base name
            fetchPokemon(pokemonName)
                .catch(error => {
                    console.log('[Pokemon Stats] First attempt failed, trying base name:', baseName);
                    if (baseName && baseName !== pokemonName) {
                        return fetchPokemon(baseName);
                    } else {
                        throw error;
                    }
                })
                .catch(error => {
                    console.error('[Pokemon Stats] All fetch attempts failed:', error);
                    const bodyEl = document.getElementById('pokemon-stats-body');
                    if (bodyEl) {
                        bodyEl.innerHTML = 
                            '<div class="pokemon-stats-error">❌ Could not load stats for this Pokemon.<br>Note: Some mega evolutions and special forms may not be available in PokeAPI.</div>';
                    }
                });
        } catch (error) {
            console.error('[Pokemon Stats] CRITICAL ERROR in showPokemonStats:', error);
        }
    };
    
    /**
     * Close the Pokemon stats modal
     */
    window.closePokemonStats = function() {
        try {
            console.log('[Pokemon Stats] closePokemonStats called');
            const modal = document.getElementById('pokemon-stats-modal');
            if (modal) {
                modal.style.display = 'none';
                console.log('[Pokemon Stats] Modal hidden');
            } else {
                console.warn('[Pokemon Stats] Modal not found when trying to close');
            }
        } catch (error) {
            console.error('[Pokemon Stats] ERROR in closePokemonStats:', error);
        }
    };
    
    // Use event delegation ONLY for pokemon sprites - don't interfere with Gradio buttons
    let listenersSetup = false;
    function setupPokemonSpriteListeners() {
        try {
            if (listenersSetup) {
                console.log('[Pokemon Stats] Listeners already setup, skipping');
                return;
            }
            
            console.log('[Pokemon Stats] Setting up sprite click listeners');
            listenersSetup = true;
            
            // Only listen for clicks on pokemon sprites - use bubbling phase (default) to not interfere
            document.addEventListener('click', function(e) {
                try {
                    // Log all clicks for debugging
                    const target = e.target;
                    const spriteDiv = target.closest('.pokemon-sprite-modern');
                    
                    if (spriteDiv) {
                        console.log('[Pokemon Stats] Click detected on sprite div:', {
                            target: target.tagName,
                            targetClass: target.className,
                            spriteDiv: spriteDiv,
                            hasDataAttrs: spriteDiv.hasAttribute('data-pokemon-name')
                        });
                        
                        const pokemonName = spriteDiv.getAttribute('data-pokemon-name');
                        const baseName = spriteDiv.getAttribute('data-base-name');
                        
                        console.log('[Pokemon Stats] Data attributes:', {pokemonName, baseName});
                        
                        if (pokemonName) {
                            console.log('[Pokemon Stats] Calling showPokemonStats with:', {pokemonName, baseName});
                            e.preventDefault();
                            e.stopPropagation();
                            window.showPokemonStats(pokemonName, baseName);
                            return false;
                        } else {
                            console.warn('[Pokemon Stats] Sprite div found but no data-pokemon-name attribute!');
                            console.log('[Pokemon Stats] Sprite div attributes:', Array.from(spriteDiv.attributes).map(a => `${a.name}="${a.value}"`));
                        }
                    }
                } catch (error) {
                    console.error('[Pokemon Stats] ERROR in click handler:', error);
                }
            }, false);
            
            console.log('[Pokemon Stats] Click listener attached to document');
            
            // Check if any sprites exist
            const existingSprites = document.querySelectorAll('.pokemon-sprite-modern');
            console.log('[Pokemon Stats] Existing sprites found:', existingSprites.length);
            if (existingSprites.length > 0) {
                existingSprites.forEach((sprite, idx) => {
                    const name = sprite.getAttribute('data-pokemon-name');
                    const base = sprite.getAttribute('data-base-name');
                    console.log(`[Pokemon Stats] Sprite ${idx}:`, {name, base});
                });
            }
        } catch (error) {
            console.error('[Pokemon Stats] ERROR in setupPokemonSpriteListeners:', error);
            listenersSetup = false; // Reset so we can try again
        }
    }
    
    // Setup listeners when ready
    console.log('[Pokemon Stats] Document ready state:', document.readyState);
    if (document.readyState === 'loading') {
        console.log('[Pokemon Stats] Waiting for DOMContentLoaded');
        document.addEventListener('DOMContentLoaded', function() {
            console.log('[Pokemon Stats] DOMContentLoaded fired');
            setupPokemonSpriteListeners();
        });
    } else {
        console.log('[Pokemon Stats] Document already ready, setting up listeners immediately');
        setupPokemonSpriteListeners();
    }
    
    // Also try after delays for Gradio's dynamic loading
    setTimeout(function() {
        console.log('[Pokemon Stats] Delayed setup attempt 1 (1000ms)');
        setupPokemonSpriteListeners();
    }, 1000);
    
    setTimeout(function() {
        console.log('[Pokemon Stats] Delayed setup attempt 2 (2000ms)');
        setupPokemonSpriteListeners();
    }, 2000);
    
    // Use MutationObserver to detect when new sprites are added
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                const hasNewSprites = Array.from(mutation.addedNodes).some(node => {
                    if (node.nodeType === 1) { // Element node
                        return node.classList && node.classList.contains('pokemon-sprite-modern') ||
                               node.querySelector && node.querySelector('.pokemon-sprite-modern');
                    }
                    return false;
                });
                
                if (hasNewSprites) {
                    console.log('[Pokemon Stats] New sprites detected via MutationObserver');
                    const newSprites = document.querySelectorAll('.pokemon-sprite-modern');
                    console.log('[Pokemon Stats] Total sprites now:', newSprites.length);
                    newSprites.forEach((sprite, idx) => {
                        const name = sprite.getAttribute('data-pokemon-name');
                        const base = sprite.getAttribute('data-base-name');
                        console.log(`[Pokemon Stats] New sprite ${idx}:`, {name, base});
                    });
                }
            }
        });
    });
    
    // Start observing
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    console.log('[Pokemon Stats] MutationObserver started');
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            console.log('[Pokemon Stats] Escape key pressed');
            window.closePokemonStats();
        }
    });
    
    console.log('[Pokemon Stats] Initialization complete');
    
    // Test function to verify script is loaded
    window.testPokemonStats = function() {
        console.log('[Pokemon Stats] TEST FUNCTION CALLED - Script is working!');
        alert('Pokemon Stats script is loaded! Check console for details.');
        const sprites = document.querySelectorAll('.pokemon-sprite-modern');
        console.log('[Pokemon Stats] TEST: Found', sprites.length, 'sprites');
        sprites.forEach((s, i) => {
            console.log(`[Pokemon Stats] TEST Sprite ${i}:`, {
                name: s.getAttribute('data-pokemon-name'),
                base: s.getAttribute('data-base-name'),
                classes: s.className
            });
        });
    };
    console.log('[Pokemon Stats] Test function available: window.testPokemonStats()');
} catch (error) {
    console.error('[Pokemon Stats] CRITICAL ERROR during initialization:', error);
    console.error('[Pokemon Stats] Error stack:', error.stack);
}
})();
console.log('[Pokemon Stats] ====== SCRIPT COMPLETE ======');

