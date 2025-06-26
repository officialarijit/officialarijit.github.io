// Publications loading functionality
document.addEventListener('DOMContentLoaded', function() {
    loadPublications();
    setupPublicationFilter();
});

let allPublications = [];
let filteredPublications = [];

async function loadPublications() {
    const publicationsList = document.getElementById('publications-list');
    
    try {
        // Fetch publications data from JSON file
        const response = await fetch('data/publications.json');
        if (!response.ok) {
            throw new Error('Failed to fetch publications');
        }
        
        const data = await response.json();
        allPublications = data.publications;
        filteredPublications = [...allPublications];
        
        // Clear loading state
        publicationsList.innerHTML = '';
        
        // Group publications by year
        const publicationsByYear = groupPublicationsByYear(filteredPublications);
        
        // Display publications
        displayPublications(publicationsByYear);
        
        // Update filter stats
        updateFilterStats();
        
    } catch (error) {
        console.error('Error loading publications:', error);
        publicationsList.innerHTML = `
            <div class="error-message">
                <p>Failed to load publications. Please try again later.</p>
                <a href="#" onclick="loadPublications()">Retry</a>
            </div>
        `;
    }
}

function setupPublicationFilter() {
    const searchInput = document.getElementById('publication-search');
    const clearBtn = document.getElementById('clear-search');
    
    // Search input event listener
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        filterPublications(searchTerm);
        
        // Show/hide clear button
        if (searchTerm.length > 0) {
            clearBtn.classList.add('show');
        } else {
            clearBtn.classList.remove('show');
        }
    });
    
    // Clear button event listener
    clearBtn.addEventListener('click', function() {
        searchInput.value = '';
        filterPublications('');
        this.classList.remove('show');
        searchInput.focus();
    });
    
    // Keyboard shortcuts
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            filterPublications('');
            clearBtn.classList.remove('show');
        }
    });
}

function filterPublications(searchTerm) {
    if (searchTerm === '') {
        filteredPublications = [...allPublications];
    } else {
        filteredPublications = allPublications.filter(publication => {
            const title = publication.title.toLowerCase();
            const authors = publication.authors.toLowerCase();
            const journal = publication.journal.toLowerCase();
            const year = publication.year.toString();
            
            return title.includes(searchTerm) || 
                   authors.includes(searchTerm) || 
                   journal.includes(searchTerm) || 
                   year.includes(searchTerm);
        });
    }
    
    // Re-display filtered publications
    const publicationsList = document.getElementById('publications-list');
    publicationsList.innerHTML = '';
    
    if (filteredPublications.length > 0) {
        const publicationsByYear = groupPublicationsByYear(filteredPublications);
        displayPublications(publicationsByYear);
    } else {
        // Show no results message
        publicationsList.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>No publications found</h3>
                <p>Try adjusting your search terms or browse all publications.</p>
                <button onclick="clearSearch()" class="btn btn-primary">Show All Publications</button>
            </div>
        `;
    }
    
    updateFilterStats();
}

function updateFilterStats() {
    const filterResults = document.getElementById('filter-results');
    const totalPublications = allPublications.length;
    const filteredCount = filteredPublications.length;
    
    if (filteredCount === totalPublications) {
        filterResults.textContent = `Showing all ${totalPublications} publications`;
    } else {
        filterResults.textContent = `Showing ${filteredCount} of ${totalPublications} publications`;
    }
}

function clearSearch() {
    const searchInput = document.getElementById('publication-search');
    const clearBtn = document.getElementById('clear-search');
    
    searchInput.value = '';
    filterPublications('');
    clearBtn.classList.remove('show');
    searchInput.focus();
}

function groupPublicationsByYear(publications) {
    const grouped = {};
    
    publications.forEach(pub => {
        const year = parseInt(pub.year); // Convert to number for proper sorting
        if (!grouped[year]) {
            grouped[year] = [];
        }
        grouped[year].push(pub);
    });
    
    // Sort years in descending order (newest first)
    const sortedYears = Object.keys(grouped)
        .map(year => parseInt(year))
        .sort((a, b) => b - a);
    
    // Create new object with sorted years
    const sortedGrouped = {};
    sortedYears.forEach(year => {
        sortedGrouped[year] = grouped[year];
    });
    
    return sortedGrouped;
}

function displayPublications(publicationsByYear) {
    const publicationsList = document.getElementById('publications-list');
    
    // Get years and sort them in descending order
    const years = Object.keys(publicationsByYear)
        .map(year => parseInt(year))
        .sort((a, b) => b - a);
    
    years.forEach(year => {
        const yearPublications = publicationsByYear[year];
        
        // Create year header
        const yearHeader = document.createElement('div');
        yearHeader.className = 'publication-year-header';
        yearHeader.innerHTML = `<h3>${year}</h3>`;
        publicationsList.appendChild(yearHeader);
        
        // Add publications for this year
        yearPublications.forEach(publication => {
            const publicationElement = createPublicationElement(publication);
            publicationsList.appendChild(publicationElement);
        });
    });
}

function createPublicationElement(publication) {
    const publicationDiv = document.createElement('div');
    publicationDiv.className = 'publication-item';
    
    // Format citation count
    const citationText = publication.citations === 1 ? 'citation' : 'citations';
    
    publicationDiv.innerHTML = `
        <div class="publication-content">
            <h3>${publication.title}</h3>
            <p class="publication-authors">${publication.authors}</p>
            <p class="publication-journal">${publication.journal}</p>
            <div class="publication-actions">
                <span class="citation-count">
                    <i class="fas fa-quote-left"></i>
                    ${publication.citations} ${citationText}
                </span>
                ${publication.links.paper ? `<a href="${publication.links.paper}" target="_blank" class="view-paper-link"><i class="fas fa-external-link-alt"></i> View Paper</a>` : ''}
            </div>
            ${publication.links.code ? `<div class="publication-links"><a href="${publication.links.code}" target="_blank"><i class="fas fa-code"></i> Code</a></div>` : ''}
        </div>
    `;
    
    return publicationDiv;
} 