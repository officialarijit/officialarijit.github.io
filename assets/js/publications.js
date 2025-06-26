// Publications loading functionality
document.addEventListener('DOMContentLoaded', function() {
    loadPublications();
});

async function loadPublications() {
    const publicationsList = document.getElementById('publications-list');
    
    try {
        // Fetch publications data from JSON file
        const response = await fetch('data/publications.json');
        if (!response.ok) {
            throw new Error('Failed to fetch publications');
        }
        
        const data = await response.json();
        const publications = data.publications;
        
        // Clear loading state
        publicationsList.innerHTML = '';
        
        // Group publications by year
        const publicationsByYear = groupPublicationsByYear(publications);
        
        // Display publications
        displayPublications(publicationsByYear);
        
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
    
    Object.keys(publicationsByYear).forEach(year => {
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
            <div class="publication-metrics">
                <span class="citation-count">
                    <i class="fas fa-quote-left"></i>
                    ${publication.citations} ${citationText}
                </span>
            </div>
            <div class="publication-links">
                ${publication.links.paper ? `<a href="${publication.links.paper}" target="_blank"><i class="fas fa-external-link-alt"></i> View Paper</a>` : ''}
                ${publication.links.code ? `<a href="${publication.links.code}" target="_blank"><i class="fas fa-code"></i> Code</a>` : ''}
            </div>
        </div>
    `;
    
    return publicationDiv;
} 