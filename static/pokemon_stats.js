/**
 * Pokemon Stats Modal JavaScript
 * 
 * Handles displaying Pokemon stats from PokeAPI when clicking on Pokemon sprites.
 * This file is separated from app.py for better organization and maintainability.
 */

console.log('[Pokemon Stats] ====== SCRIPT STARTING ======');
(function() {
    'use strict';
    try {
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
    
    // Simple inline SVG icons per type (used as faint watermark behind artwork)
    const TYPE_ICON_SVGS = {
        normal: '<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="40" fill="rgba(0,0,0,0.2)"/></svg>',
        fire: '<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M50 10 C30 30 40 40 35 55 C30 70 40 85 50 90 C60 85 70 70 65 55 C60 40 70 30 50 10 Z" fill="rgba(255,80,40,0.4)"/></svg>',
        water: '<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M50 10 C40 30 30 45 30 60 C30 75 40 85 50 85 C60 85 70 75 70 60 C70 45 60 30 50 10 Z" fill="rgba(80,144,255,0.4)"/></svg>',
        electric: '<svg viewBox="0 0 100 100" aria-hidden="true"><polygon points="45,10 25,55 45,55 35,90 75,45 55,45 70,10" fill="rgba(248,208,48,0.5)"/></svg>',
        grass: '<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M50 10 C30 30 25 50 30 65 C35 80 45 90 50 90 C55 90 65 80 70 65 C75 50 70 30 50 10 Z" fill="rgba(120,200,80,0.4)"/></svg>',
        ice: '<svg viewBox="0 0 100 100" aria-hidden="true"><polygon points="50,5 60,25 82,25 68,40 75,60 50,50 25,60 32,40 18,25 40,25" fill="rgba(152,216,216,0.5)"/></svg>',
        fighting: '<svg viewBox="0 0 100 100" aria-hidden="true"><rect x="30" y="30" width="40" height="40" rx="8" fill="rgba(192,48,40,0.5)"/></svg>',
        poison: '<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="35" cy="40" r="12" fill="rgba(160,64,160,0.5)"/><circle cx="65" cy="40" r="12" fill="rgba(160,64,160,0.3)"/><circle cx="50" cy="65" r="15" fill="rgba(160,64,160,0.4)"/></svg>',
        ground: '<svg viewBox="0 0 100 100" aria-hidden="true"><polygon points="10,70 40,40 60,65 75,50 90,70" fill="rgba(224,192,104,0.6)"/></svg>',
        flying: '<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M10 60 C30 40 40 40 60 50 C70 55 80 55 90 50 C80 65 65 80 45 80 C30 80 20 70 10 60 Z" fill="rgba(168,144,240,0.5)"/></svg>',
        psychic: '<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="28" fill="none" stroke="rgba(248,88,136,0.5)" stroke-width="8"/><circle cx="50" cy="50" r="8" fill="rgba(248,88,136,0.5)"/></svg>',
        bug: '<svg viewBox="0 0 100 100" aria-hidden="true"><ellipse cx="50" cy="55" rx="20" ry="25" fill="rgba(168,184,32,0.6)"/><line x1="30" y1="35" x2="20" y2="25" stroke="rgba(168,184,32,0.6)" stroke-width="4"/><line x1="70" y1="35" x2="80" y2="25" stroke="rgba(168,184,32,0.6)" stroke-width="4"/></svg>',
        rock: '<svg viewBox="0 0 100 100" aria-hidden="true"><polygon points="20,70 35,30 65,25 80,55 60,80 35,80" fill="rgba(184,160,56,0.6)"/></svg>',
        ghost: '<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M20 70 C20 40 30 20 50 20 C70 20 80 40 80 70 L72 62 64 70 56 62 48 70 40 62 32 70 Z" fill="rgba(112,88,152,0.5)"/></svg>',
        dragon: '<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M20 60 C20 30 40 20 60 25 C70 27 75 20 80 15 C78 25 75 35 70 40 C80 45 85 60 75 70 C65 80 45 80 35 72 C25 64 20 60 20 60 Z" fill="rgba(112,56,248,0.5)"/></svg>',
        dark: '<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M65 15 C50 18 40 30 40 45 C40 60 50 72 65 75 C55 82 42 82 32 75 C20 67 15 53 18 40 C22 25 35 15 50 12 C55 11 60 12 65 15 Z" fill="rgba(112,88,72,0.7)"/></svg>',
        steel: '<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="28" fill="rgba(184,184,208,0.7)"/><circle cx="50" cy="50" r="16" fill="rgba(240,240,248,0.9)"/></svg>',
        fairy: '<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M50 20 L58 38 L78 40 L62 52 L66 72 L50 62 L34 72 L38 52 L22 40 L42 38 Z" fill="rgba(238,153,172,0.6)"/></svg>'
    };
    
    /**
     * Check if Pokemon is a Mega evolution
     * @param {string} name - Pokemon name
     * @returns {boolean}
     */
    function isMegaPokemon(name) {
        return name.toLowerCase().includes('mega');
    }
    
    /**
     * Get background color based on Pokemon types
     * @param {Array} types - Array of type objects
     * @returns {string} CSS gradient or color string
     */
    function getTypeBackground(types) {
        if (!types || types.length === 0) {
            return 'linear-gradient(135deg, #f0f0f0 0%, #e8e8e8 100%)';
        }
        
        const typeColors = {
            'normal': '#A8A878',
            'fire': '#F08030',
            'water': '#6890F0',
            'electric': '#F8D030',
            'grass': '#78C850',
            'ice': '#98D8D8',
            'fighting': '#C03028',
            'poison': '#A040A0',
            'ground': '#E0C068',
            'flying': '#A890F0',
            'psychic': '#F85888',
            'bug': '#A8B820',
            'rock': '#B8A038',
            'ghost': '#705898',
            'dragon': '#7038F8',
            'dark': '#705848',
            'steel': '#B8B8D0',
            'fairy': '#EE99AC'
        };
        
        const primaryType = types[0].type.name;
        const primaryColor = typeColors[primaryType] || '#A8A878';
        
        if (types.length > 1) {
            // Dual type - create gradient
            const secondaryType = types[1].type.name;
            const secondaryColor = typeColors[secondaryType] || '#A8A878';
            return `linear-gradient(135deg, ${primaryColor} 0%, ${secondaryColor} 100%)`;
        } else {
            // Single type - use gradient with lighter shade
            return `linear-gradient(135deg, ${primaryColor} 0%, ${primaryColor}dd 100%)`;
        }
    }
    
    /**
     * Get color for stat value - below 70 red, 90 yellow, 100 green, 120 bright green, 130+ blue teal
     * @param {number} statValue - The stat value (0-255)
     * @returns {string} RGB color string for background bar
     */
    function getStatColor(statValue) {
        if (statValue < 70) {
            // Below 70: Bright red
            const intensity = Math.min(1, statValue / 70); // 0 to 1
            const red = 255;
            const green = Math.round(50 * intensity); // 0 -> 50
            const blue = Math.round(50 * intensity); // 0 -> 50
            return `rgb(${red}, ${green}, ${blue})`;
        } else if (statValue < 90) {
            // 70-90: Transition from red to yellow (deeper yellow for visibility)
            const normalized = (statValue - 70) / 20; // 0 to 1
            const red = 255;
            const green = Math.round(50 + 150 * normalized); // 50 -> 200 (deeper yellow)
            const blue = Math.round(50 * (1 - normalized)); // 50 -> 0
            return `rgb(${red}, ${green}, ${blue})`;
        } else if (statValue < 100) {
            // 90-100: Transition from yellow (deeper) to green
            const normalized = (statValue - 90) / 10; // 0 to 1
            const red = Math.round(200 * (1 - normalized)); // 200 -> 0 (deeper yellow start)
            const green = 255;
            const blue = 0;
            return `rgb(${red}, ${green}, ${blue})`;
        } else if (statValue < 120) {
            // 100-120: Transition from green to bright green
            const normalized = (statValue - 100) / 20; // 0 to 1
            const red = 0;
            const green = 255;
            const blue = Math.round(0 + 100 * normalized); // 0 -> 100 (adds cyan for brightness)
            return `rgb(${red}, ${green}, ${blue})`;
        } else if (statValue < 130) {
            // 120-130: Transition from bright green to blue teal
            const normalized = (statValue - 120) / 10; // 0 to 1
            const red = 0;
            const green = Math.round(255 * (1 - normalized * 0.3)); // 255 -> 178.5
            const blue = Math.round(100 + 155 * normalized); // 100 -> 255
            return `rgb(${red}, ${green}, ${blue})`;
        } else {
            // 130+: Blue teal
            const normalized = Math.min(1, (statValue - 130) / 125); // 0 to 1 (130-255)
            const red = 0;
            const green = Math.round(178.5 * (1 - normalized * 0.2)); // 178.5 -> 142.8
            const blue = 255;
            return `rgb(${red}, ${green}, ${blue})`;
        }
    }
    
    /**
     * Fetch Pokemon Species data from PokeAPI
     * @param {string} speciesName - Pokemon species name to fetch
     * @returns {Promise<Object>} Species data with shape, color, and egg groups
     */
    function fetchPokemonSpecies(speciesName) {
        console.log('[Pokemon Stats] Fetching Pokemon Species:', speciesName);
        const url = `${POKEAPI_BASE_URL}/pokemon-species/${speciesName}`;
        
        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    console.warn('[Pokemon Stats] Species not found:', speciesName);
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return null;
                
                const shape = data.shape?.name || null;
                const color = data.color?.name || null;
                const eggGroups = data.egg_groups?.map(eg => eg.name) || [];
                
                return {
                    shape: shape,
                    color: color,
                    eggGroups: eggGroups
                };
            })
            .catch(error => {
                console.warn('[Pokemon Stats] Error fetching species:', speciesName, error);
                return null;
            });
    }
    
    /**
     * Fetch ability data from PokeAPI
     * @param {string} abilityName - Ability name to fetch
     * @returns {Promise<string>} Ability short effect description
     */
    function fetchAbilityDescription(abilityName) {
        console.log('[Pokemon Stats] Fetching ability:', abilityName);
        const url = `${POKEAPI_BASE_URL}/ability/${abilityName}`;
        
        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    console.warn('[Pokemon Stats] Ability not found:', abilityName);
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return null;
                
                // Find English effect entry
                const effectEntry = data.effect_entries?.find(entry => 
                    entry.language?.name === 'en'
                );
                
                // Return short_effect if available, otherwise effect
                return effectEntry?.short_effect || effectEntry?.effect || null;
            })
            .catch(error => {
                console.warn('[Pokemon Stats] Error fetching ability:', abilityName, error);
                return null;
            });
    }
    
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
                const artwork = data.sprites.other['official-artwork']?.front_default || 
                              data.sprites.front_default || 
                              data.sprites.other?.dream_world?.front_default || '';
                const stats = data.stats;
                const types = data.types || [];
                const abilities = data.abilities || [];
                const height = (data.height / 10).toFixed(1); // Convert to meters
                const weight = (data.weight / 10).toFixed(1); // Convert to kg
                
                // Calculate total stats
                const totalStats = stats.reduce((sum, stat) => sum + stat.base_stat, 0);
                
                console.log('[Pokemon Stats] Parsed data:', {name, artwork: !!artwork, statsCount: stats.length, types: types.length, abilities: abilities.length});
                
                const isMega = isMegaPokemon(name);
                const typeBackground = getTypeBackground(types);
                const primaryType = (types[0] && types[0].type && types[0].type.name) || 'normal';
                const typeIconSvg = TYPE_ICON_SVGS[primaryType] || TYPE_ICON_SVGS['normal'];
                
                let statsHTML = '';
                
                // Pokemon image with type icon watermark
                if (artwork) {
                    statsHTML += `<div class="pokemon-stats-art" style="background: ${typeBackground};">`;
                    statsHTML += `<div class="pokemon-type-icon">${typeIconSvg}</div>`;
                    statsHTML += `<img src="${artwork}" alt="${name}" />`;
                    if (isMega) {
                        statsHTML += '<div class="mega-symbol">MEGA</div>';
                    }
                    statsHTML += '</div>';
                }
                
                // Fetch species data and ability descriptions in parallel
                const speciesPromise = fetchPokemonSpecies(data.species.name);
                const abilityPromises = abilities.map(ability => 
                    fetchAbilityDescription(ability.ability.name).then(description => ({
                        ability: ability,
                        description: description
                    }))
                );
                
                return Promise.all([speciesPromise, ...abilityPromises]).then(results => {
                    const speciesData = results[0];
                    const abilityData = results.slice(1);
                    
                    // Physical stats (Height, Weight, Types, Shape, Color, Egg Groups)
                    statsHTML += '<div class="pokemon-physical-stats">';
                    statsHTML += `<div class="physical-stat-item"><span class="physical-stat-label">Height</span><span class="physical-stat-value">${height}m</span></div>`;
                    statsHTML += `<div class="physical-stat-divider"></div>`;
                    statsHTML += `<div class="physical-stat-item"><span class="physical-stat-label">Weight</span><span class="physical-stat-value">${weight}kg</span></div>`;
                    if (types.length > 0) {
                        statsHTML += `<div class="physical-stat-divider"></div>`;
                        statsHTML += '<div class="physical-stat-item physical-stat-types">';
                        statsHTML += '<span class="physical-stat-label">Type</span>';
                        statsHTML += '<div class="pokemon-types-inline">';
                        types.forEach(type => {
                            const typeName = type.type.name;
                            statsHTML += `<span class="pokemon-type-badge pokemon-type-${typeName}">${typeName.charAt(0).toUpperCase() + typeName.slice(1)}</span>`;
                        });
                        statsHTML += '</div>';
                        statsHTML += '</div>';
                    }
                    if (speciesData) {
                        if (speciesData.shape) {
                            statsHTML += `<div class="physical-stat-divider"></div>`;
                            statsHTML += `<div class="physical-stat-item"><span class="physical-stat-label">Shape</span><span class="physical-stat-value">${speciesData.shape.charAt(0).toUpperCase() + speciesData.shape.slice(1)}</span></div>`;
                        }
                        if (speciesData.color) {
                            statsHTML += `<div class="physical-stat-divider"></div>`;
                            statsHTML += `<div class="physical-stat-item"><span class="physical-stat-label">Color</span><span class="physical-stat-value">${speciesData.color.charAt(0).toUpperCase() + speciesData.color.slice(1)}</span></div>`;
                        }
                        if (speciesData.eggGroups && speciesData.eggGroups.length > 0) {
                            statsHTML += `<div class="physical-stat-divider"></div>`;
                            statsHTML += '<div class="physical-stat-item physical-stat-egggroups">';
                            statsHTML += '<span class="physical-stat-label">Egg Group</span>';
                            statsHTML += '<div class="egg-groups-inline">';
                            speciesData.eggGroups.forEach(eggGroup => {
                                statsHTML += `<span class="egg-group-badge">${eggGroup.charAt(0).toUpperCase() + eggGroup.slice(1)}</span>`;
                            });
                            statsHTML += '</div>';
                            statsHTML += '</div>';
                        }
                    }
                    statsHTML += '</div>';
                    
                    // Build abilities HTML with descriptions stored as data attributes
                    if (abilities.length > 0) {
                        statsHTML += '<div class="pokemon-abilities-section">';
                        statsHTML += '<span class="pokemon-abilities-label">Abilities</span>';
                        statsHTML += '<div class="pokemon-abilities">';
                        abilityData.forEach((abilityResult) => {
                            const {ability, description} = abilityResult;
                            const abilityName = ability.ability.name;
                            const isHidden = ability.is_hidden;
                            const displayName = abilityName.charAt(0).toUpperCase() + abilityName.slice(1).replace(/-/g, ' ');
                            
                            const descriptionAttr = description ? ` data-ability-description="${description.replace(/"/g, '&quot;')}"` : '';
                            statsHTML += `<span class="pokemon-ability-badge ${isHidden ? 'pokemon-ability-hidden' : ''}"${descriptionAttr}>${displayName}${isHidden ? ' <span class="hidden-label">(Hidden)</span>' : ''}</span>`;
                        });
                        statsHTML += '</div></div>';
                    }
                    
                    statsHTML += '<ul class="pokemon-stats-list">';
                    
                    stats.forEach((stat, index) => {
                        const statName = stat.stat.name;
                        const statValue = stat.base_stat;
                        const displayName = STAT_NAMES[statName] || statName;
                        const statColor = getStatColor(statValue);
                        const statPercentage = Math.min(100, (statValue / 200) * 100);
                        
                        statsHTML += `
                            <li class="pokemon-stat-item stat-row" style="animation-delay: ${index * 50}ms;">
                                <div class="stat-row-content">
                                    <span class="pokemon-stat-name">${displayName}</span>
                                    <div class="stat-bar-container">
                                        <div class="stat-bar" style="width: ${statPercentage}%; background-color: ${statColor};"></div>
                                    </div>
                                    <span class="pokemon-stat-value" style="color: ${statColor};">${statValue}</span>
                                </div>
                            </li>
                        `;
                    });
                    
                    statsHTML += '</ul>';
                    
                    // Add Total stat after all individual stats
                    const totalStatColor = getStatColor(totalStats);
                    const totalStatPercentage = Math.min(100, (totalStats / 600) * 100); // Max total is around 600
                    statsHTML += `
                        <div class="pokemon-stat-item stat-row" style="animation-delay: ${stats.length * 50}ms; margin-top: 0.5rem; padding-top: 0.75rem; border-top: 2px solid var(--border);">
                            <div class="stat-row-content">
                                <span class="pokemon-stat-name">Total</span>
                                <div class="stat-bar-container">
                                    <div class="stat-bar" style="width: ${totalStatPercentage}%; background-color: ${totalStatColor};"></div>
                                </div>
                                <span class="pokemon-stat-value total-stats" style="color: ${totalStatColor};">${totalStats}</span>
                            </div>
                        </div>
                    `;
                    
                    const bodyEl = document.getElementById('pokemon-stats-body');
                    const titleEl = document.getElementById('pokemon-stats-title');
                    
                    if (bodyEl && titleEl) {
                        bodyEl.innerHTML = statsHTML;
                        titleEl.textContent = name.charAt(0).toUpperCase() + name.slice(1).replace(/-/g, ' ');
                        
                        // Create tooltips for ability badges with descriptions (hover only)
                        const abilityBadges = bodyEl.querySelectorAll('.pokemon-ability-badge[data-ability-description]');
                        abilityBadges.forEach(badge => {
                            const description = badge.getAttribute('data-ability-description');
                            if (description) {
                                const tooltip = document.createElement('div');
                                tooltip.className = 'pokemon-ability-tooltip';
                                tooltip.textContent = description;
                                badge.appendChild(tooltip);
                                
                                // Adjust tooltip position to stay within card bounds
                                badge.addEventListener('mouseenter', function() {
                                    setTimeout(() => {
                                        const rect = badge.getBoundingClientRect();
                                        const tooltipRect = tooltip.getBoundingClientRect();
                                        const cardContent = badge.closest('.pokemon-stats-content');
                                        const cardRect = cardContent ? cardContent.getBoundingClientRect() : { left: 0, right: window.innerWidth };
                                        
                                        // Calculate if tooltip overflows
                                        const badgeCenterX = rect.left + (rect.width / 2);
                                        const tooltipHalfWidth = tooltipRect.width / 2;
                                        const tooltipLeft = badgeCenterX - tooltipHalfWidth;
                                        const tooltipRight = badgeCenterX + tooltipHalfWidth;
                                        
                                        // Reset positioning
                                        tooltip.style.left = '50%';
                                        tooltip.style.right = 'auto';
                                        
                                        // Adjust if goes beyond left edge
                                        if (tooltipLeft < cardRect.left + 10) {
                                            const offset = (cardRect.left + 10) - tooltipLeft;
                                            tooltip.style.left = `calc(50% - ${offset}px)`;
                                        }
                                        
                                        // Adjust if goes beyond right edge
                                        if (tooltipRight > cardRect.right - 10) {
                                            const offset = tooltipRight - (cardRect.right - 10);
                                            tooltip.style.left = `calc(50% + ${offset}px)`;
                                        }
                                    }, 10);
                                });
                            }
                        });
                        
                        console.log('[Pokemon Stats] Stats displayed successfully');
                    } else {
                        console.error('[Pokemon Stats] ERROR: Modal elements missing when updating!');
                    }
                });
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
                        <div class="pokemon-card-top">
                            <div class="pokeball-icon"></div>
                            <div class="pokemon-stats-header">
                                <h2 class="pokemon-stats-title" id="pokemon-stats-title">Loading...</h2>
                                <button class="pokemon-stats-close" id="pokemon-stats-close-btn">&times;</button>
                            </div>
                        </div>
                        <div class="pokemon-card-body">
                            <div id="pokemon-stats-body">
                                <div class="pokemon-stats-loading">Loading stats...</div>
                            </div>
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

